import sys

import pytest

from ferrule.config import Settings


@pytest.fixture
def ws(tmp_path):
    w = tmp_path / "ws"
    w.mkdir()
    return w


@pytest.fixture
def settings(ws, tmp_path):
    return Settings(
        workspace=ws,
        home=tmp_path / "home",
        allowlist={"python": None, "git": ["status"]},
        test_command=[sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
        command_timeout=60,
    )
