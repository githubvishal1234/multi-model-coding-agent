import pytest
from helpers import call, make_ctx

# `python` resolves through PATH, like a model-issued command would.
WRITE_FILE = ["python", "-c", "open('ran.txt', 'w').write('yes')"]


@pytest.mark.parametrize("argv", [["rm", "-rf", "."], ["curl", "http://example.com"],
                                  ["powershell", "-c", "dir"], ["git", "push"]])
def test_disallowed_commands_never_ask_or_run(settings, argv):
    ctx, approver = make_ctx(settings, default=True)
    r = call(ctx, "run_command", argv=argv)
    assert not r.ok and r.error.startswith("refused") and approver.requests == []


def test_allowlisted_command_denied_does_not_run(settings, ws):
    ctx, approver = make_ctx(settings, [False])
    r = call(ctx, "run_command", argv=WRITE_FILE)
    assert not r.ok and not (ws / "ran.txt").exists()
    assert approver.requests[0].kind == "run_command"


def test_allowlisted_command_approved_runs(settings, ws):
    ctx, _ = make_ctx(settings, [True])
    r = call(ctx, "run_command", argv=WRITE_FILE)
    assert r.ok and "exit code: 0" in r.output and (ws / "ran.txt").read_text() == "yes"


def test_command_timeout(settings):
    ctx, _ = make_ctx(settings.model_copy(update={"command_timeout": 1}), [True])
    r = call(ctx, "run_command", argv=["python", "-c", "__import__('time').sleep(10)"])
    assert not r.ok and "timed out" in r.error


def test_auto_safe_skips_approval_for_git_status_only(settings, ws):
    ctx, approver = make_ctx(settings.model_copy(update={"approval": "auto_safe"}), [False])
    call(ctx, "run_command", argv=["git", "status"])
    assert approver.requests == []
    call(ctx, "run_command", argv=WRITE_FILE)
    assert len(approver.requests) == 1


@pytest.fixture
def project(ws):
    (ws / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    (ws / "test_bad.py").write_text("def test_bad():\n    assert 1 == 2\n")
    return ws


def test_run_tests_reports_failure(settings, project):
    ctx, approver = make_ctx(settings, [True])
    r = call(ctx, "run_tests")
    assert not r.ok and "1 failed, 1 passed" in r.output
    assert approver.requests[0].kind == "run_tests"


def test_run_tests_reports_pass_and_auto_safe_skips_approval(settings, project):
    (project / "test_bad.py").unlink()
    ctx, approver = make_ctx(settings.model_copy(update={"approval": "auto_safe"}))
    r = call(ctx, "run_tests")
    assert r.ok and "1 passed" in r.output and approver.requests == []


def test_run_tests_denied(settings, project):
    ctx, _ = make_ctx(settings, [False])
    assert "rejected" in call(ctx, "run_tests").error
