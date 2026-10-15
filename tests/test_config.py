import json

import pytest
from pydantic import ValidationError

from ferrule.config import Settings


def test_load_dotenv(tmp_path):
    from ferrule.config import load_dotenv
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\n\nGROQ_API_KEY=gsk_abc123\nexport GEMINI_API_KEY='g-key'\n"
        'OPENROUTER_API_KEY="sk-or-xyz"\nCEREBRAS_API_KEY=\nFERRULE_PROFILE=quality  # note\n'
        "ALREADY=from-file\nnot a line\n", encoding="utf-8")
    environ = {"ALREADY": "real"}
    loaded = load_dotenv(env_file, environ)
    assert environ == {"ALREADY": "real", "GROQ_API_KEY": "gsk_abc123", "GEMINI_API_KEY": "g-key",
                       "OPENROUTER_API_KEY": "sk-or-xyz", "FERRULE_PROFILE": "quality"}
    assert "CEREBRAS_API_KEY" not in loaded and "ALREADY" not in loaded  # empty / already set
    assert load_dotenv(tmp_path / "missing.env", environ) == []


def test_defaults():
    s = Settings.from_env({})
    assert s.max_steps == 20 and s.approval == "ask" and s.supports_tools is True


def test_env_overrides_defaults(tmp_path):
    s = Settings.from_env({
        "FERRULE_MAX_STEPS": "5",
        "FERRULE_APPROVAL": "auto_safe",
        "FERRULE_SUPPORTS_TOOLS": "false",
        "FERRULE_HOME": str(tmp_path),
        "FERRULE_TEST_COMMAND": json.dumps(["pytest", "-x"]),
        "FERRULE_ALLOWLIST": json.dumps({"pytest": None}),
    })
    assert s.max_steps == 5
    assert s.approval == "auto_safe"
    assert s.supports_tools is False
    assert s.home == tmp_path
    assert s.test_command == ["pytest", "-x"]
    assert s.allowlist == {"pytest": None}


def test_cli_overrides_env_and_none_is_ignored():
    s = Settings.from_env({"FERRULE_MODEL": "a"}, model="b", max_steps=None)
    assert s.model == "b" and s.max_steps == 20


@pytest.mark.parametrize("env", [
    {"FERRULE_MAX_STEPS": "0"},
    {"FERRULE_APPROVAL": "always"},
    {"FERRULE_TEST_COMMAND": "not json"},
])
def test_invalid_values_raise(env):
    with pytest.raises((ValidationError, ValueError)):
        Settings.from_env(env)
