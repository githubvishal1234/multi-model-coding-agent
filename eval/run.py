"""Run an evaluation: python -m eval.run --config eval/configs/example.yaml

Each task runs in a fresh temporary copy of its repo snapshot. The agent's approvals are
auto-granted inside that copy (commands still go through the allowlist), then the task's
check decides pass/fail. Results go to <output_dir>/<run_id>/ as results.csv, results.md
and meta.json.
"""

import argparse
import asyncio
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import httpx
import yaml
from pydantic import BaseModel, ConfigDict, Field

from eval.tasks import Task, load_tasks
from ferrule.agent import Agent, RunResult
from ferrule.config import Settings
from ferrule.events import ScriptedApprover
from ferrule.providers import OpenAICompatProvider

ROOT = Path(__file__).resolve().parent.parent
CHECK_OUTPUT_CHARS = 600


class EvalConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    tasks: list[str] = Field(min_length=1)  # globs relative to the config file
    agent: Literal["ferrule", "reference", "noop"] = "ferrule"
    model: str = "qwen2.5-coder:7b"
    base_url: str = "http://127.0.0.1:11434/v1"
    supports_tools: bool = True
    max_steps: int = Field(15, ge=1)
    model_timeout: float = 300
    command_timeout: float = 120
    check_timeout: float = 120
    params: dict = Field(default_factory=dict)  # sent with every model request
    output_dir: str = "../results"  # relative to the config file


class Row(BaseModel):
    task: str
    task_class: str
    passed: bool
    agent_status: str
    steps: int
    seconds: float
    prompt_tokens: int | None
    completion_tokens: int | None
    failure_reason: str


AgentFn = Callable[[Task, Settings], Awaitable[RunResult]]


def expand(argv: list[str]) -> list[str]:
    return [a.replace("{python}", sys.executable) for a in argv]


# --- agents ---

def ferrule_agent(cfg: EvalConfig) -> AgentFn:
    async def run(task: Task, settings: Settings) -> RunResult:
        provider = OpenAICompatProvider(cfg.base_url, cfg.model, timeout=cfg.model_timeout,
                                        params=cfg.params)
        try:
            agent = Agent(provider, settings, ScriptedApprover(default=True))
            return await agent.run(task.instruction)
        finally:
            await provider.aclose()
    return run


async def reference_agent(task: Task, settings: Settings) -> RunResult:
    """Copies the task's hand-written solution. Proves the check can pass."""
    if task.solution is None:
        return RunResult("no_solution", "task has no solution directory")
    shutil.copytree(task.path(task.solution), settings.workspace, dirs_exist_ok=True)
    return RunResult("done", "copied reference solution", 1)


async def noop_agent(task: Task, settings: Settings) -> RunResult:
    """Changes nothing. Proves the check fails on the untouched snapshot."""
    return RunResult("done", "no changes", 0)


def make_agent(cfg: EvalConfig) -> AgentFn:
    return {"ferrule": lambda: ferrule_agent(cfg), "reference": lambda: reference_agent,
            "noop": lambda: noop_agent}[cfg.agent]()


# --- running ---

def run_check(task: Task, workspace: Path, timeout: float) -> tuple[bool, str]:
    if task.check.files:
        shutil.copytree(task.path(task.check.files), workspace, dirs_exist_ok=True)
    try:
        proc = subprocess.run(expand(task.check.command), cwd=workspace, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=timeout,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return False, f"check timed out after {timeout:g}s"
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == task.check.expect_exit, output[-CHECK_OUTPUT_CHARS:]


async def run_task(task: Task, agent: AgentFn, cfg: EvalConfig) -> Row:
    with tempfile.TemporaryDirectory(prefix=f"ferrule-eval-{task.id}-",
                                     ignore_cleanup_errors=True) as tmp:
        workspace = Path(tmp) / "repo"
        shutil.copytree(task.path(task.repo), workspace)
        settings = Settings(
            workspace=workspace, home=Path(tmp) / "home", model=cfg.model,
            supports_tools=cfg.supports_tools, max_steps=cfg.max_steps,
            model_timeout=cfg.model_timeout, command_timeout=cfg.command_timeout,
            test_command=expand(task.test_command),
        )
        start = time.perf_counter()
        try:
            result = await agent(task, settings)
        except Exception as e:  # one broken task must not end the whole run
            result = RunResult("crash", f"{type(e).__name__}: {e}")
        seconds = round(time.perf_counter() - start, 2)
        passed, check_output = run_check(task, workspace, cfg.check_timeout)

    if passed:
        reason = ""
    elif result.status != "done":
        reason = f"agent {result.status}: {' '.join(result.answer.split())[:250]}"
    else:  # the end of test output holds the summary, so keep the tail
        reason = f"check failed: ...{' '.join(check_output.split())[-250:]}"
    return Row(task=task.id, task_class=task.task_class, passed=passed,
               agent_status=result.status, steps=result.steps, seconds=seconds,
               prompt_tokens=result.usage.get("prompt_tokens"),
               completion_tokens=result.usage.get("completion_tokens"),
               failure_reason=reason)


# --- metadata and reports ---

def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def model_digest(cfg: EvalConfig) -> str | None:
    """Ollama digest of the model, so results name the exact weights. None if unknown."""
    if cfg.agent != "ferrule":
        return None
    try:
        tags = httpx.get(cfg.base_url.removesuffix("/v1") + "/api/tags", timeout=5).json()
    except (httpx.HTTPError, ValueError):
        return None
    return next((m.get("digest") for m in tags.get("models", []) if m.get("name") == cfg.model),
                None)


def metadata(cfg: EvalConfig, tasks: list[Task]) -> dict:
    config = cfg.model_dump(mode="json")
    now = datetime.now(UTC)
    return {
        "run_id": f"{now:%Y%m%dT%H%M%SZ}_{cfg.name}",
        "date": now.isoformat(timespec="seconds"),
        "config_name": cfg.name,
        "config_hash": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12],
        "config": config,
        "agent": cfg.agent,
        "model": cfg.model if cfg.agent == "ferrule" else None,
        "model_digest": model_digest(cfg),
        "tasks": [t.id for t in tasks],
        "code_commit": _git("rev-parse", "HEAD"),
        "code_dirty": bool(_git("status", "--porcelain")),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }


def markdown(meta: dict, rows: list[Row]) -> str:
    passed = sum(r.passed for r in rows)
    lines = [
        f"# Eval results: {meta['config_name']}",
        "",
        f"- date: {meta['date']}",
        f"- agent: {meta['agent']}, model: {meta['model']} (digest {meta['model_digest']})",
        f"- config hash: {meta['config_hash']}, code commit: {meta['code_commit']}"
        + (" (uncommitted changes)" if meta["code_dirty"] else ""),
        f"- **passed: {passed}/{len(rows)}**",
        "",
        "| task | class | passed | agent status | steps | seconds | tokens in/out | failure |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        failure = r.failure_reason.replace("|", "\\|")
        lines.append(f"| {r.task} | {r.task_class} | {'yes' if r.passed else 'no'} | "
                     f"{r.agent_status} | {r.steps} | {r.seconds} | "
                     f"{r.prompt_tokens}/{r.completion_tokens} | {failure} |")
    by_class: dict[str, list[bool]] = {}
    for r in rows:
        by_class.setdefault(r.task_class, []).append(r.passed)
    lines += ["", "| class | passed |", "|---|---|"]
    lines += [f"| {c} | {sum(v)}/{len(v)} |" for c, v in sorted(by_class.items())]
    return "\n".join(lines) + "\n"


def write_reports(out_dir: Path, meta: dict, rows: list[Row]) -> Path:
    run_dir = out_dir / meta["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(Row.model_fields))
        writer.writeheader()
        writer.writerows(r.model_dump() for r in rows)
    (run_dir / "results.md").write_text(markdown(meta, rows), encoding="utf-8")
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return run_dir


def load_config(path: Path, **overrides) -> EvalConfig:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    data.update({k: v for k, v in overrides.items() if v is not None})
    return EvalConfig.model_validate(data)


async def run_eval(cfg: EvalConfig, base: Path, only: list[str] | None = None,
                   agent: AgentFn | None = None, progress=print) -> tuple[dict, list[Row]]:
    tasks = load_tasks(cfg.tasks, base)
    if only:
        tasks = [t for t in tasks if t.id in only]
    agent = agent or make_agent(cfg)
    rows = []
    for task in tasks:
        progress(f"[{len(rows) + 1}/{len(tasks)}] {task.id} ...")
        rows.append(await run_task(task, agent, cfg))
        progress(f"    {'PASS' if rows[-1].passed else 'FAIL'} {rows[-1].failure_reason}")
    return metadata(cfg, tasks), rows


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(errors="replace")
    p = argparse.ArgumentParser(prog="python -m eval.run")
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--agent", choices=["ferrule", "reference", "noop"],
                   help="override the config: reference/noop verify that tasks are well-formed")
    p.add_argument("--model")
    p.add_argument("--task", action="append", help="run only this task id (repeatable)")
    args = p.parse_args(argv)

    cfg = load_config(args.config, agent=args.agent, model=args.model)
    base = args.config.resolve().parent
    meta, rows = asyncio.run(run_eval(cfg, base, args.task,
                                      progress=lambda s: print(s, flush=True)))
    run_dir = write_reports((base / cfg.output_dir).resolve(), meta, rows)
    print()
    print(markdown(meta, rows))
    print(f"reports: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
