import asyncio
from pathlib import Path

import pytest

from ferrule.providers import BadResponse, RateLimited, Reply, Unavailable
from ferrule.registry import Registry
from ferrule.router import (
    NoModelAvailable,
    RoutedProvider,
    Router,
    classify,
    estimate_repo_tokens,
)
from ferrule.safety import Redactor

# --- classifier (F13) ---

@pytest.mark.parametrize("task,expected", [
    ("test_median_even fails. Fix the bug in stats.py", "debug"),
    ("Traceback (most recent call last): ... ZeroDivisionError", "debug"),
    ("Write pytest tests for slugify() in test_text.py", "tests"),
    ("Rename calc_total to compute_total everywhere", "multi_file_refactor"),
    ("Explain what sync_orders() does", "explain"),
    ("Which function reads the database URL?", "explain"),
    ("Add a route /version to app.py", "boilerplate"),
    ("Add a --lines option to wordcount.py", "boilerplate"),
    ("Add a docstring to area()", "small_edit"),
])
def test_classify(task, expected):
    assert classify(task) == expected


def test_big_repo_is_long_context():
    assert classify("Add a docstring to area()", repo_tokens=50_000) == "long_context"


def test_estimate_repo_tokens(tmp_path):
    (tmp_path / "a.py").write_text("x" * 4000)
    (tmp_path / "img.png").write_bytes(b"\0" * 4000)
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "big.py").write_text("x" * 40000)
    assert estimate_repo_tokens(tmp_path) == 1000


def test_eval_task_labels_vs_classifier():
    """Report-only: how often the rules agree with the hand labels on the eval tasks."""
    from eval.tasks import load_tasks
    tasks = load_tasks(["*/task.yaml"], Path(__file__).parent.parent / "eval" / "tasks")
    agree = sum(classify(t.instruction) == t.task_class for t in tasks)
    assert agree >= 1  # rules are a starting point; the number is shown in the Phase 5 notes
    print(f"classifier agrees with {agree}/{len(tasks)} eval task labels")


# --- ranking and exclusions (F14, F18, N5) ---

REG = Registry.model_validate({
    "providers": {
        "ollama": {"base_url": "http://local/v1", "local": True},
        "fasthost": {"base_url": "http://fast/v1", "api_key_env": "FAST_KEY",
                     "caps": {"requests_per_minute": 2, "requests_per_day": 3}},
        "bighost": {"base_url": "http://big/v1", "api_key_env": "BIG_KEY"},
    },
    "models": [
        {"name": "small", "provider": "ollama", "params_b": 3, "context": 8000},
        {"name": "medium", "provider": "ollama", "params_b": 7, "context": 32000},
        {"name": "notools", "provider": "ollama", "params_b": 6, "context": 16000,
         "supports_tools": False},
        {"name": "fast70", "provider": "fasthost", "params_b": 70, "context": 128000},
        {"name": "big400", "provider": "bighost", "params_b": 400, "context": 256000},
    ],
})
for _m in REG.models:  # every test model supports tools unless it says otherwise
    if _m.name != "notools":
        _m.supports_tools = True
KEYS = {"FAST_KEY": "k1", "BIG_KEY": "k2"}


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def names(router, cls="debug", **kw):
    return [m.name for m in router.ranked(cls, **kw)[0]]


def test_balanced_is_local_first_then_hosted():
    assert names(Router(REG, KEYS)) == ["medium", "small", "big400", "fast70"]


def test_quality_and_fast_profiles():
    assert names(Router(REG, KEYS, profile="quality")) == ["big400", "fast70", "medium", "small"]
    assert names(Router(REG, KEYS, profile="fast")) == ["small", "medium", "fast70", "big400"]


def test_eval_scores_outrank_size():
    reg = REG.model_copy(deep=True)
    next(m for m in reg.models if m.name == "small").scores = {"debug": 0.9}
    next(m for m in reg.models if m.name == "medium").scores = {"debug": 0.4}
    assert names(Router(reg, KEYS))[:2] == ["small", "medium"]
    # scores are per class: with no "tests" score, size decides again
    assert names(Router(reg, KEYS), cls="tests")[:2] == ["medium", "small"]


def test_exclusions_have_reasons():
    r = Router(REG, {"BIG_KEY": "k2"}, installed={"small", "notools"}, local_fit={"small"})
    usable, skipped = r.ranked("debug", context_needed=10_000)
    assert [m.name for m in usable] == ["big400"]
    assert skipped["fast70"] == "no API key (FAST_KEY not set)"
    assert skipped["medium"] == "not installed"
    assert skipped["notools"] == "no native tool calling"
    assert skipped["small"].startswith("context 8000")


def test_prompted_mode_allows_models_without_tools():
    assert "notools" in names(Router(REG, KEYS, native_tools=False))


def test_local_only_never_lists_hosted():
    assert names(Router(REG, KEYS, local_only=True)) == ["medium", "small"]


def test_fit_and_speed_filters():
    r = Router(REG, KEYS, local_fit={"small", "medium"}, too_slow={"medium"})
    assert names(r)[0] == "small"


def test_per_minute_daily_and_session_caps():
    clock = Clock()
    r = Router(REG, KEYS, local_only=False, clock=clock)
    fast = next(m for m in REG.models if m.name == "fast70")
    r.record_request(fast)
    r.record_request(fast)
    assert r.ranked("debug")[1]["fast70"] == "fasthost per-minute cap reached"
    clock.t += 61
    assert "fast70" in names(r)
    r.record_request(fast)
    assert r.ranked("debug")[1]["fast70"] == "fasthost daily cap reached"
    session = Router(REG, KEYS, max_hosted_requests=1)
    session.record_request(fast)
    assert "session cap" in session.ranked("debug")[1]["big400"]


def test_cooldown_expires():
    clock = Clock()
    r = Router(REG, KEYS, clock=clock, cooldown_s=60)
    r.cool_down("ollama")
    assert names(r)[0] == "big400"
    clock.t += 61
    assert names(r)[0] == "medium"


# --- routed provider: fallback, escalation, notice, redaction (F15, F16, F17, N6, N3) ---

class Fake:
    def __init__(self, name, outcomes):
        self.name, self.outcomes, self.calls = name, list(outcomes), []

    async def chat(self, messages, tools=None, on_token=None):
        self.calls.append(messages)
        out = self.outcomes.pop(0) if len(self.outcomes) > 1 else self.outcomes[0]
        if isinstance(out, Exception):
            raise out
        return out


class Audit:
    def __init__(self):
        self.lines = []

    def write(self, event, **fields):
        self.lines.append((event, fields))


def routed(fakes, router=None, **kw):
    router = router or Router(REG, KEYS, **kw)
    events, audit = [], Audit()
    rp = RoutedProvider(router, "debug", make_provider=lambda m, p: fakes[m.name],
                        redact=Redactor({"MY_TOKEN": "supersecret123"}))
    rp.attach(events.append, audit)
    return rp, events, audit


def chat(rp, content="hi"):
    return asyncio.run(rp.chat([{"role": "user", "content": content}]))


def test_first_choice_is_logged_with_reason():
    rp, events, audit = routed({"medium": Fake("medium", [Reply(content="ok")])})
    assert chat(rp).content == "ok"
    routing = [e.data for e in events if e.kind == "routing"]
    assert routing[0]["chosen"] == "medium" and routing[0]["reason"] == "best available model"
    assert audit.lines[0][0] == "routing"


def test_fallback_on_rate_limit_and_outage():
    fakes = {"medium": Fake("medium", [Unavailable("down")]),
             "small": Fake("small", [RateLimited("429")]),
             "big400": Fake("big400", [Reply(content="from big")])}
    rp, events, _ = routed(fakes)
    assert chat(rp).content == "from big"
    reasons = [e.data["reason"] for e in events if e.kind == "routing"]
    assert reasons[1].startswith("fallback after ollama Unavailable")
    assert rp.model == "big400"


def test_bad_model_id_is_marked_failed():
    rp, _, _ = routed({"medium": Fake("medium", [BadResponse("HTTP 404")]),
                       "small": Fake("small", [Reply(content="ok")])})
    chat(rp)
    assert "medium" in rp.router.failed


def test_all_failing_raises_with_reasons():
    rp, _, _ = routed({n: Fake(n, [Unavailable("x")]) for n in ("medium", "small")},
                      local_only=True)
    with pytest.raises(NoModelAvailable, match="medium"):
        chat(rp)


def test_escalate_moves_to_next_model_and_stops_at_end():
    rp, events, _ = routed({}, local_only=True)
    assert rp.model == "medium"
    assert rp.escalate("tests failed twice") and rp.model == "small"
    assert not rp.escalate("still failing") and rp.model == "small"
    assert "escalated from medium: tests failed twice" in [
        e.data["reason"] for e in events if e.kind == "routing"]


def test_notice_and_redaction_only_for_hosted():
    fakes = {"medium": Fake("medium", [Reply(content="ok")]),
             "big400": Fake("big400", [Reply(content="ok")])}
    rp, events, _ = routed(fakes)
    chat(rp, "token supersecret123")
    assert fakes["medium"].calls[0][0]["content"] == "token supersecret123"  # local: unchanged
    assert not [e for e in events if e.kind == "notice"]
    rp.tried.add("small")  # skip the other local model so escalation goes to a hosted one
    assert rp.escalate("need stronger") and rp.model == "big400"
    chat(rp, "token supersecret123")
    chat(rp, "again")
    assert fakes["big400"].calls[0][0]["content"] == "token [REDACTED]"
    notices = [e.data["message"] for e in events if e.kind == "notice"]
    assert len(notices) == 1 and "leaves this machine" in notices[0]


def test_local_only_mode_makes_zero_hosted_calls():
    fakes = {n: Fake(n, [Unavailable("x")]) for n in ("medium", "small")}
    fakes["big400"] = Fake("big400", [Reply(content="hosted")])
    rp, _, _ = routed(fakes, local_only=True)
    with pytest.raises(NoModelAvailable):
        chat(rp)
    assert fakes["big400"].calls == []


def test_hosted_cap_reached_mid_session_switches_model():
    router = Router(REG, KEYS, local_only=False, max_hosted_requests=1)
    fakes = {"big400": Fake("big400", [Reply(content="a")]),
             "medium": Fake("medium", [Unavailable("x")]),
             "small": Fake("small", [Unavailable("x")])}
    rp, _, _ = routed(fakes, router=router)
    rp.tried |= {"medium", "small"}
    assert chat(rp).content == "a"
    with pytest.raises(NoModelAvailable, match="session cap"):
        chat(rp)


# --- agent + router together (F15) ---

def run_agent(settings, fakes, **router_kw):
    from ferrule.agent import Agent
    from ferrule.events import ScriptedApprover
    rp = RoutedProvider(Router(REG, KEYS, **router_kw), "debug",
                        make_provider=lambda m, p: fakes[m.name])
    events = []
    agent = Agent(rp, settings.model_copy(update={"supports_tools": False}),
                  ScriptedApprover(default=True), events.append)
    return asyncio.run(agent.run("fix it")), events, rp


def test_agent_escalates_after_repeated_invalid_output(settings, ws):
    from helpers import tool_reply
    (ws / "a.py").write_text("x = 1\n")
    fakes = {"medium": Fake("medium", [tool_reply("no_such_tool")]),
             "small": Fake("small", [tool_reply("write_file", path="a.py", content="x = 2\n"),
                                     tool_reply("run_tests"), Reply(content="done")])}
    result, events, rp = run_agent(settings.model_copy(update={"max_invalid": 1}), fakes,
                                   local_only=True)
    assert result.status == "done" and rp.model == "small"
    assert (ws / "a.py").read_text() == "x = 2\n"
    assert any("switched to small" in e.data.get("message", "") for e in events)


def test_agent_escalates_after_tests_fail_twice(settings, ws):
    from helpers import tool_reply
    (ws / "test_a.py").write_text("def test_a():\n    assert False\n")
    fakes = {"medium": Fake("medium", [tool_reply("run_tests")]),
             "small": Fake("small", [Reply(content="giving up")])}
    _, events, rp = run_agent(settings, fakes, local_only=True)
    assert rp.model == "small"
    reasons = [e.data["reason"] for e in events if e.kind == "routing"]
    assert reasons[-1] == "escalated from medium: tests failed twice in a row"


def test_agent_without_router_still_stops_on_invalid_output(settings):
    from helpers import MockProvider, tool_reply

    from ferrule.agent import Agent
    from ferrule.events import ScriptedApprover
    agent = Agent(MockProvider(tool_reply("nope")),
                  settings.model_copy(update={"supports_tools": False, "max_invalid": 1}),
                  ScriptedApprover(default=True))
    assert asyncio.run(agent.run("x")).status == "invalid_output"


def test_keys_never_in_logs():
    keys = {"FAST_KEY": "fast-secret-value", "BIG_KEY": "big-secret-value"}
    router = Router(REG, keys, profile="quality")
    rp, events, audit = routed({"big400": Fake("big400", [Reply(content="ok")])}, router=router)
    chat(rp)
    text = repr(events) + repr(audit.lines) + repr(rp._client(rp.current))
    assert "fast-secret-value" not in text and "big-secret-value" not in text
