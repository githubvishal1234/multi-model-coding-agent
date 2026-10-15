import asyncio
import json

import pytest
from helpers import MockProvider, tool_reply

from ferrule.agent import Agent, ParseError, parse_tool_calls
from ferrule.events import ScriptedApprover
from ferrule.providers import Reply, Unavailable
from ferrule.undo import undo

# --- parsing ---

def native(name, args, id="c1"):
    return Reply(tool_calls=[{"id": id, "type": "function",
                              "function": {"name": name, "arguments": json.dumps(args)}}])


def test_parse_native():
    [c] = parse_tool_calls(native("read_file", {"path": "a"}))
    assert (c.name, c.args, c.id) == ("read_file", {"path": "a"}, "c1")


@pytest.mark.parametrize("content", [
    '```tool\n{"tool": "read_file", "args": {"path": "a"}}\n```',
    'Let me look.\n```json\n{"tool": "read_file", "args": {"path": "a"}}\n```',
])
def test_parse_prompted(content):
    [c] = parse_tool_calls(Reply(content=content))
    assert (c.name, c.args) == ("read_file", {"path": "a"})


@pytest.mark.parametrize("content", [
    # Seen from qwen2.5-coder:7b in native mode: the call arrives as plain content.
    '{"name": "read_file", "arguments": {"path": "a"}}',
    '{"name": "read_file", "arguments": "{\\"path\\": \\"a\\"}"}',
    # Seen from qwen2.5-coder:7b in prompted mode: a Python-style single-quoted string.
    "```tool\n{\"tool\": \"read_file\", \"args\": {\"path\": 'a'}}\n```",
    # Seen from qwen2.5-coder:7b in prompted mode: args written flat next to "tool".
    '```tool\n{"tool": "read_file", "path": "a"}\n```',
    # Seen from qwen2.5-coder:7b in prompted mode: the fence label is the tool name.
    '```read_file\n{\n  "path": "a"\n}\n```',
])
def test_parse_lenient_formats_seen_from_real_models(content):
    [c] = parse_tool_calls(Reply(content=content), tool_names={"read_file"})
    assert (c.name, c.args) == ("read_file", {"path": "a"})


@pytest.mark.parametrize("content", ["All done.", '```json\n{"name": "config"}\n```',
                                     '{"name": "config"}', "{not a call}",
                                     '```python\n{"path": "a"}\n```'])
def test_parse_no_tool_call(content):
    assert parse_tool_calls(Reply(content=content), tool_names={"read_file"}) == []


@pytest.mark.parametrize("reply", [
    Reply(content='```tool\n{"tool": "read_file", "args": {path: a}}\n```'),
    Reply(content='```tool\n{"tool": "read_file", "args": "a"}\n```'),
    Reply(content="```tool\n{'tool': 'read_file', 'args': {path}}\n```"),
    # Seen from qwen2.5-coder:7b: a raw newline inside a string in a "name"/"arguments" call.
    Reply(content='```json\n{"name": "edit_file", "arguments": {"new": "a\n    b"}}\n```'),
    Reply(tool_calls=[{"id": "1", "function": {"name": "read_file", "arguments": "{bad"}}]),
])
def test_parse_malformed(reply):
    with pytest.raises(ParseError):
        parse_tool_calls(reply)


# --- loop ---

def run(provider, settings, approver=None, task="do it", plan=False, **overrides):
    settings = settings.model_copy(update={"supports_tools": False, **overrides})
    events = []
    agent = Agent(provider, settings, approver or ScriptedApprover(default=True), events.append)
    return asyncio.run(agent.run(task, plan=plan)), events


def test_loop_runs_tools_until_done(settings, ws):  # F9
    (ws / "a.txt").write_text("hello")
    provider = MockProvider(tool_reply("read_file", path="a.txt"),
                            tool_reply("write_file", path="b.txt", content="hi"),
                            tool_reply("run_tests"),
                            Reply(content="Created b.txt."))
    result, events = run(provider, settings)
    assert result.status == "done" and result.steps == 4 and result.answer == "Created b.txt."
    assert (ws / "b.txt").read_text() == "hi"
    assert [e.kind for e in events if e.kind != "token"] == \
        ["tool_call", "tool_result"] * 3 + ["done"]
    assert "Result of read_file:\nhello" in provider.calls[1]["messages"][-1]["content"]
    roles = [m["role"] for m in result.messages]
    assert roles == ["system", "user"] + ["assistant", "user"] * 3 + ["assistant"]
    assert result.messages[-1] == {"role": "assistant", "content": "Created b.txt."}


# --- finish checks: one nudge each before a final answer is accepted ---

def notices(events):
    return [e.data["message"] for e in events if e.kind == "notice"]


def test_final_answer_without_changes_is_nudged_once(settings, ws):
    # Seen in eval: the model describes the fix in text instead of editing the file.
    (ws / "cart.py").write_text("x = 1\n")
    provider = MockProvider(Reply(content="Change x = 1 to x = 2."),
                            tool_reply("edit_file", path="cart.py", old="x = 1", new="x = 2"),
                            tool_reply("run_tests"),
                            Reply(content="Fixed."))
    result, events = run(provider, settings)
    assert result.status == "done" and (ws / "cart.py").read_text() == "x = 2\n"
    [notice] = notices(events)
    assert notice.startswith("You have not changed") and "```tool" in notice


def test_question_only_task_finishes_after_one_nudge(settings):
    provider = MockProvider(Reply(content="It returns 4."))
    result, events = run(provider, settings)
    assert result.status == "done" and result.answer == "It returns 4."
    assert len(provider.calls) == 2 and len(notices(events)) == 1


def test_untested_changes_are_nudged_once(settings, ws):
    # Seen in eval: edits used a name that was never imported; running tests would show it.
    (ws / "a.py").write_text("x = 1\n")
    provider = MockProvider(tool_reply("edit_file", path="a.py", old="x = 1", new="x = 2"),
                            Reply(content="Done."),
                            tool_reply("run_tests"),
                            Reply(content="Done, tests run."))
    result, events = run(provider, settings)
    assert result.status == "done" and result.answer == "Done, tests run."
    [notice] = notices(events)
    assert "run_tests" in notice
    assert '"tool": "run_tests"' in notice and "write_file" not in notice  # matching example
    assert any(e.kind == "tool_call" and e.data["tool"] == "run_tests" for e in events)


def test_nudges_do_not_repeat(settings, ws):
    (ws / "a.py").write_text("x = 1\n")
    provider = MockProvider(tool_reply("edit_file", path="a.py", old="x = 1", new="x = 2"),
                            Reply(content="Done."))  # repeats, never runs tests
    result, events = run(provider, settings)
    assert result.status == "done" and len(notices(events)) == 1


def test_native_mode_nudge_has_no_fence_reminder(settings):
    result, events = run(MockProvider(Reply(content="ok")), settings, supports_tools=True)
    assert result.status == "done" and "```tool" not in notices(events)[0]


def test_native_mode_sends_tool_messages(settings, ws):
    (ws / "a.txt").write_text("hello")
    provider = MockProvider(native("read_file", {"path": "a.txt"}), Reply(content="ok"))
    result, _ = run(provider, settings, supports_tools=True)
    assert result.status == "done"
    assert provider.calls[0]["tools"] and provider.calls[0]["tools"][0]["type"] == "function"
    sent = provider.calls[1]["messages"]
    assert sent[-2]["tool_calls"][0]["id"] == "c1"
    assert sent[-1] == {"role": "tool", "tool_call_id": "c1", "content": "hello"}


def test_loop_stops_at_max_steps(settings, ws):  # F10
    (ws / "a.txt").write_text("x")
    provider = MockProvider(tool_reply("read_file", path="a.txt"))
    result, events = run(provider, settings, max_steps=4)
    assert result.status == "max_steps" and len(provider.calls) == 4
    assert events[-1].kind == "stopped"


def test_invalid_calls_are_retried_then_stop(settings):  # F5
    provider = MockProvider(tool_reply("no_such_tool"))
    result, _ = run(provider, settings, max_invalid=2)
    assert result.status == "invalid_output"
    assert len(provider.calls) == 3  # 2 errors fed back, the 3rd invalid reply stops the loop
    feedback = [m for m in provider.calls[-1]["messages"] if m["content"].startswith("Error:")]
    assert len(feedback) == 2 and "unknown tool" in feedback[0]["content"]


def test_valid_call_resets_invalid_counter(settings, ws):
    (ws / "a.txt").write_text("x")
    bad, good = tool_reply("read_file"), tool_reply("read_file", path="a.txt")
    provider = MockProvider(bad, good, bad, good, Reply(content="done"))
    result, _ = run(provider, settings, max_invalid=1)
    assert result.status == "done"


def test_plan_rejected_changes_nothing(settings, ws):  # F11
    provider = MockProvider(Reply(content="1. create b.txt"),
                            tool_reply("write_file", path="b.txt", content="x"))
    approver = ScriptedApprover([False], default=True)
    result, events = run(provider, settings, approver, plan=True)
    assert result.status == "plan_rejected"
    assert len(provider.calls) == 1 and provider.calls[0]["tools"] is None
    assert not (ws / "b.txt").exists()
    assert approver.requests[0].kind == "plan"


def test_plan_approved_then_runs(settings, ws):
    provider = MockProvider(Reply(content="1. create b.txt"),
                            tool_reply("write_file", path="b.txt", content="x"),
                            Reply(content="done"))
    result, _ = run(provider, settings, plan=True)
    assert result.status == "done" and (ws / "b.txt").exists()
    assert "Approved plan:\n1. create b.txt" in provider.calls[1]["messages"][-1]["content"]


def test_model_timeout(settings):
    class Slow(MockProvider):
        async def chat(self, *a, **kw):
            await asyncio.sleep(5)

    result, _ = run(Slow(Reply()), settings, model_timeout=0.05)
    assert result.status == "timeout"
    assert result.messages[-1]["content"].endswith("[model call timed out]")


def test_timeout_keeps_partial_reply(settings):
    class Rambling(MockProvider):
        async def chat(self, messages, tools=None, on_token=None):
            on_token("I will write the tests now")
            await asyncio.sleep(5)

    result, _ = run(Rambling(Reply()), settings, model_timeout=0.05)
    assert result.messages[-1]["content"] == "I will write the tests now\n[model call timed out]"


def test_provider_error_stops(settings):
    result, _ = run(MockProvider(Unavailable("ollama down")), settings)
    assert result.status == "provider_error" and "ollama down" in result.answer


def test_audit_log_records_run(settings, ws):
    (ws / "a.txt").write_text("x")
    run(MockProvider(tool_reply("read_file", path="a.txt"), Reply(content="ok")), settings)
    log = (settings.home / "audit.log").read_text(encoding="utf-8")
    events = [json.loads(line)["event"] for line in log.splitlines()]
    assert events == ["run_start", "tool_call", "tool_result", "run_end"]


# --- undo (F12) ---

def test_undo_restores_edits_and_removes_created_files(settings, ws):
    (ws / "a.txt").write_text("original\n")
    provider = MockProvider(tool_reply("edit_file", path="a.txt", old="original", new="changed"),
                            tool_reply("edit_file", path="a.txt", old="changed", new="twice"),
                            tool_reply("write_file", path="sub/b.txt", content="new"),
                            Reply(content="done"))
    run(provider, settings)
    assert (ws / "a.txt").read_text() == "twice\n" and (ws / "sub" / "b.txt").exists()

    restored = undo(settings)
    assert len(restored) == 2
    assert (ws / "a.txt").read_text() == "original\n"
    assert not (ws / "sub" / "b.txt").exists()
    assert undo(settings) == []


def test_read_only_run_leaves_no_checkpoint(settings, ws):
    (ws / "a.txt").write_text("x")
    run(MockProvider(tool_reply("read_file", path="a.txt"), Reply(content="ok")), settings)
    assert undo(settings) == []
