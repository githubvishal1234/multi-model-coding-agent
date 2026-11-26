from ferrule.cli import main


def test_missing_workspace_fails_before_calling_a_model(tmp_path, capsys):
    missing = tmp_path / "does-not-exist"
    assert main(["run", "do something", "--workspace", str(missing)]) == 2
    assert "does not exist" in capsys.readouterr().err


# --- --json mode (VS Code extension protocol) ---

import io  # noqa: E402
import json  # noqa: E402

import pytest  # noqa: E402
from helpers import MockProvider  # noqa: E402

from ferrule.providers import Reply  # noqa: E402


def native(name, args):
    return Reply(tool_calls=[{"id": "c1", "type": "function",
                              "function": {"name": name, "arguments": json.dumps(args)}}])


@pytest.mark.parametrize("approved", [True, False])
def test_json_mode_streams_events_and_reads_approvals(tmp_path, capsys, monkeypatch, approved):
    ws = tmp_path / "ws"
    ws.mkdir()
    monkeypatch.setenv("FERRULE_HOME", str(tmp_path / "home"))
    provider = MockProvider(native("write_file", {"path": "a.txt", "content": "hi\n"}),
                            Reply(content="Done."))

    async def fake_build(settings, task, extra_params=None):
        return provider
    provider.aclose = lambda: _noop()
    monkeypatch.setattr("ferrule.cli.build_provider", fake_build)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"id": 1, "approved": approved})
                                                 + "\n"))
    main(["run", "make a.txt", "--workspace", str(ws), "--json"])
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    [ask] = [m for m in lines if m["type"] == "approval"]
    assert ask["id"] == 1 and ask["kind"] == "write_file" and "a.txt" in ask["summary"]
    assert any(m["type"] == "event" and m["kind"] == "tool_call" for m in lines)
    assert lines[-1]["type"] == "result" and lines[-1]["status"] == "done"
    assert (ws / "a.txt").exists() == approved


async def _noop():
    return None
