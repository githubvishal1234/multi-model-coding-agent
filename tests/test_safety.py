import json
import os
import sys

import pytest

from ferrule.safety import AuditLog, Redactor, SafetyError, check_command, resolve


@pytest.fixture
def outside(tmp_path):
    d = tmp_path / "outside"
    d.mkdir()
    (d / "secret.txt").write_text("outside data")
    return d


def test_resolve_inside(ws):
    (ws / "src").mkdir()
    (ws / "src" / "a.py").write_text("x")
    assert resolve(ws, "src/a.py") == ws.resolve() / "src" / "a.py"
    assert resolve(ws, "src/../src/a.py") == ws.resolve() / "src" / "a.py"
    assert resolve(ws, "new/file.txt").name == "file.txt"  # not-yet-existing paths are fine


@pytest.mark.parametrize("path", ["../outside/secret.txt", "src/../../outside/secret.txt", ".."])
def test_dotdot_escape_rejected(ws, outside, path):
    with pytest.raises(SafetyError, match="outside the workspace"):
        resolve(ws, path)


def test_absolute_path_rejected(ws, outside):
    with pytest.raises(SafetyError):
        resolve(ws, str(outside / "secret.txt"))
    system_file = r"C:\Windows\win.ini" if sys.platform == "win32" else "/etc/passwd"
    with pytest.raises(SafetyError):
        resolve(ws, system_file)


def test_symlink_escape_rejected(ws, outside):
    try:
        os.symlink(outside, ws / "link", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("creating symlinks is not permitted here")
    with pytest.raises(SafetyError):
        resolve(ws, "link/secret.txt")


@pytest.mark.skipif(sys.platform != "win32", reason="junctions are Windows-only")
def test_junction_escape_rejected(ws, outside):
    import _winapi
    _winapi.CreateJunction(str(outside), str(ws / "junc"))
    with pytest.raises(SafetyError):
        resolve(ws, "junc/secret.txt")


@pytest.mark.parametrize("path", [".env", "config/.env.local", "id_rsa", "keys/server.pem",
                                  "aws_credentials.json", ".git/config", ".GIT/HEAD"])
def test_secret_and_git_paths_rejected(ws, path):
    with pytest.raises(SafetyError):
        resolve(ws, path)


def test_env_example_allowed(ws):
    assert resolve(ws, ".env.example").name == ".env.example"


ALLOW = {"python": ["-m"], "git": ["status", "diff"], "pytest": None}


@pytest.mark.parametrize("argv", [
    [], ["rm", "-rf", "x"], ["curl", "http://x"], ["powershell", "-c", "x"],
    ["git", "push"], ["git"], ["python", "-c", "print(1)"],
    ["pytest", "x; rm -rf /"], ["pytest", "a && b"], ["pytest", "$(whoami)"],
    ["/usr/bin/python", "-m", "x"], [r"C:\evil\pytest.exe"],
])
def test_command_rejected(argv):
    with pytest.raises(SafetyError):
        check_command(argv, ALLOW)


@pytest.mark.parametrize("argv,prog", [
    (["git", "status"], "git"), (["pytest", "-q", "tests/"], "pytest"),
    (["python", "-m", "pytest"], "python"), (["PYTEST.EXE"], "pytest"),
])
def test_command_allowed(argv, prog):
    assert check_command(argv, ALLOW) == prog


def test_redactor_strips_known_formats_and_env_values():
    redact = Redactor({"MY_API_KEY": "supersecretvalue123", "PATH": "not-a-secret-value"})
    text = ("key=supersecretvalue123 openai=sk-abcdefghijklmnopqrstuvwx "
            "gh=ghp_" + "a" * 36 + " aws=AKIAABCDEFGHIJKLMNOP path=not-a-secret-value")
    out = redact(text)
    for secret in ("supersecretvalue123", "sk-abcdef", "ghp_aaa", "AKIAABCD"):
        assert secret not in out
    assert "not-a-secret-value" in out


def test_audit_log_is_json_lines_and_redacted(tmp_path):
    log = AuditLog(tmp_path / "a" / "audit.log", Redactor({"SERVICE_TOKEN": "tok_1234567890"}))
    log.write("tool_call", tool="read_file", args={"path": "x"})
    log.write("note", text="leaked tok_1234567890")
    lines = (tmp_path / "a" / "audit.log").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    records = [json.loads(line) for line in lines]
    assert records[0]["event"] == "tool_call" and "ts" in records[0]
    assert "tok_1234567890" not in lines[1]
