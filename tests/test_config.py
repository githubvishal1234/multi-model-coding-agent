import json

import pytest
from pydantic import ValidationError

from ferrule.config import Settings


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
