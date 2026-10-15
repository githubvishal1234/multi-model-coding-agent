"""Runner tests with mock agents. No model, no network."""

import asyncio
import csv
import json
import sys
from pathlib import Path

import pytest

from eval.run import EvalConfig, markdown, run_eval, write_reports
from eval.tasks import load_task, load_tasks
from ferrule.agent import RunResult

EXAMPLE = Path(__file__).resolve().parent.parent / "configs"


def make_task(root: Path, task_id="t1", check_files=True) -> Path:
    """Task: make value.txt contain 'right'. Hidden check reads it."""
    d = root / task_id
    (d / "repo").mkdir(parents=True)
    (d / "repo" / "value.txt").write_text("wrong")
    yaml = (f"id: {task_id}\nclass: small_edit\ninstruction: set value.txt to right\n"
            "check:\n  command: ['{python}', 'check.py']\n")
    if check_files:
        (d / "check").mkdir()
        (d / "check" / "check.py").write_text(
            "import sys, pathlib\n"
            "sys.exit(0 if pathlib.Path('value.txt').read_text() == 'right' else 1)\n")
        yaml += "  files: check\n"
    (d / "task.yaml").write_text(yaml)
    return d / "task.yaml"


def cfg(**kw) -> EvalConfig:
    return EvalConfig(name="unit", tasks=["*/task.yaml"], **kw)


def run(root, agent, **kw):
    return asyncio.run(run_eval(cfg(**kw), root, agent=agent, progress=lambda *_: None))


async def fixing_agent(task, settings):
    (settings.workspace / "value.txt").write_text("right")
    return RunResult("done", "fixed", 3, {"prompt_tokens": 100, "completion_tokens": 20})


async def lazy_agent(task, settings):
    return RunResult("done", "did nothing", 1)


async def crashing_agent(task, settings):
    raise RuntimeError("boom")


async def stuck_agent(task, settings):
    return RunResult("max_steps", "stopped after 15 steps", 15)


# --- task format ---

def test_load_valid_task(tmp_path):
    task = load_task(make_task(tmp_path))
    assert task.id == "t1" and task.task_class == "small_edit"
    assert task.check.command == ["{python}", "check.py"] and task.check.files == "check"


@pytest.mark.parametrize("yaml,error", [
    ("class: debug\ninstruction: x\ncheck: {command: [a]}\n", "id"),
    ("id: t\nclass: nonsense\ninstruction: x\ncheck: {command: [a]}\n", "class"),
    ("id: t\nclass: debug\ninstruction: x\n", "check"),
    ("id: t\nclass: debug\ninstruction: x\ncheck: {command: [a]}\nsurprise: 1\n", "surprise"),
    ("id: t\nclass: debug\ninstruction: x\ncheck: {command: [a]}\nrepo: missing\n", "missing"),
])
def test_invalid_task_has_clear_error(tmp_path, yaml, error):
    (tmp_path / "repo").mkdir()
    (tmp_path / "task.yaml").write_text(yaml)
    with pytest.raises(ValueError, match=error):
        load_task(tmp_path / "task.yaml")


def test_duplicate_ids_rejected(tmp_path):
    make_task(tmp_path / "a")
    make_task(tmp_path / "b")
    with pytest.raises(ValueError, match="duplicate"):
        load_tasks(["*/*/task.yaml"], tmp_path)


def test_tasks_sorted_by_id(tmp_path):
    for tid in ("zeta", "alpha", "mid"):
        make_task(tmp_path, tid)
    assert [t.id for t in load_tasks(["*/task.yaml"], tmp_path)] == ["alpha", "mid", "zeta"]


# --- runner ---

def test_passing_agent(tmp_path):
    make_task(tmp_path)
    meta, [row] = run(tmp_path, fixing_agent)
    assert row.passed and row.failure_reason == ""
    assert (row.steps, row.prompt_tokens, row.completion_tokens) == (3, 100, 20)
    assert meta["tasks"] == ["t1"]


def test_runs_in_isolated_copy(tmp_path):
    make_task(tmp_path)
    run(tmp_path, fixing_agent)
    assert (tmp_path / "t1" / "repo" / "value.txt").read_text() == "wrong"
    assert not (tmp_path / "t1" / "repo" / "check.py").exists()


def test_failing_agent_reports_check_failure(tmp_path):
    make_task(tmp_path)
    _, [row] = run(tmp_path, lazy_agent)
    assert not row.passed and row.failure_reason.startswith("check failed")


def test_agent_stop_reason_is_reported(tmp_path):
    make_task(tmp_path)
    _, [row] = run(tmp_path, stuck_agent)
    assert not row.passed and row.agent_status == "max_steps"
    assert row.failure_reason.startswith("agent max_steps")


def test_crash_is_recorded_and_run_continues(tmp_path):
    make_task(tmp_path, "a")
    make_task(tmp_path, "b")
    calls = []

    async def crash_first(task, settings):
        calls.append(task.id)
        return await (crashing_agent if task.id == "a" else fixing_agent)(task, settings)

    _, rows = run(tmp_path, crash_first)
    assert calls == ["a", "b"]
    assert rows[0].agent_status == "crash" and "boom" in rows[0].failure_reason
    assert rows[1].passed


def test_agent_gets_task_test_command_with_python_expanded(tmp_path):
    make_task(tmp_path)
    seen = {}

    async def spy(task, settings):
        seen["settings"] = settings
        return RunResult("done")

    run(tmp_path, spy, max_steps=7)
    s = seen["settings"]
    assert s.test_command[0] == sys.executable and s.max_steps == 7
    assert s.home != s.workspace and not s.home.is_relative_to(s.workspace)


def test_check_timeout(tmp_path):
    path = make_task(tmp_path, check_files=False)
    path.write_text(path.read_text().replace(
        "['{python}', 'check.py']", "['{python}', '-c', '__import__(\"time\").sleep(10)']"))
    _, [row] = run(tmp_path, fixing_agent, check_timeout=1)
    assert not row.passed and "timed out" in row.failure_reason


# --- reports and reproducibility ---

def test_reports_written(tmp_path):
    make_task(tmp_path / "tasks")
    meta, rows = run(tmp_path / "tasks", fixing_agent)
    run_dir = write_reports(tmp_path / "out", meta, rows)
    with open(run_dir / "results.csv", encoding="utf-8") as f:
        [record] = list(csv.DictReader(f))
    assert record["task"] == "t1" and record["passed"] == "True"
    saved = json.loads((run_dir / "meta.json").read_text())
    assert saved["config_hash"] == meta["config_hash"] and saved["date"]
    assert "**passed: 1/1**" in (run_dir / "results.md").read_text()


def test_same_config_is_reproducible(tmp_path):
    make_task(tmp_path, "a")
    make_task(tmp_path, "b")
    meta1, rows1 = run(tmp_path, fixing_agent)
    meta2, rows2 = run(tmp_path, fixing_agent)
    for key in ("tasks", "config_hash", "config", "agent", "python", "platform"):
        assert meta1[key] == meta2[key]
    strip = [{k: v for k, v in r.model_dump().items() if k != "seconds"} for r in rows1]
    assert strip == [{k: v for k, v in r.model_dump().items() if k != "seconds"} for r in rows2]


def test_markdown_escapes_pipes():
    from eval.run import Row
    row = Row(task="t", task_class="debug", passed=False, agent_status="done", steps=1,
              seconds=0.1, prompt_tokens=None, completion_tokens=None,
              failure_reason="a | b")
    meta = {"config_name": "x", "date": "d", "agent": "a", "model": "m", "model_digest": None,
            "config_hash": "h", "code_commit": None, "code_dirty": False}
    assert "a \\| b" in markdown(meta, [row])


# --- every task in eval/tasks is well-formed (runs on each task you add) ---

def test_all_tasks_fail_untouched_and_pass_with_reference():
    from eval.run import load_config
    config = load_config(EXAMPLE / "example.yaml")
    for agent, expected in (("noop", False), ("reference", True)):
        _, rows = asyncio.run(run_eval(config.model_copy(update={"agent": agent}), EXAMPLE,
                                       progress=lambda *_: None))
        assert len(rows) >= 5
        wrong = [(r.task, r.failure_reason) for r in rows if r.passed != expected]
        assert not wrong, f"with --agent {agent}: {wrong}"
