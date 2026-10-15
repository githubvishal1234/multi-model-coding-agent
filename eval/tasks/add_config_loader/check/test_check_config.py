import dataclasses

import pytest

from config import Config, load_config


def test_defaults():
    c = load_config({})
    assert isinstance(c, Config) and dataclasses.is_dataclass(c)
    assert (c.host, c.port, c.debug, c.allowed_hosts) == ("127.0.0.1", 8000, False, [])


def test_values_from_env():
    c = load_config({"APP_HOST": "0.0.0.0", "APP_PORT": "9001", "APP_DEBUG": "yes",
                     "APP_ALLOWED_HOSTS": " a.com, b.com ,,c.com "})
    assert c.host == "0.0.0.0"
    assert c.port == 9001 and isinstance(c.port, int)
    assert c.debug is True
    assert c.allowed_hosts == ["a.com", "b.com", "c.com"]


@pytest.mark.parametrize("raw,expected", [
    ("1", True), ("true", True), ("TRUE", True), ("Yes", True),
    ("0", False), ("false", False), ("no", False), ("", False), ("maybe", False),
])
def test_debug_parsing(raw, expected):
    assert load_config({"APP_DEBUG": raw}).debug is expected


@pytest.mark.parametrize("raw", ["", " ", " , ,"])
def test_empty_allowed_hosts(raw):
    assert load_config({"APP_ALLOWED_HOSTS": raw}).allowed_hosts == []


@pytest.mark.parametrize("port", ["abc", "0", "65536", "-1", "80.5", ""])
def test_invalid_port_raises(port):
    with pytest.raises(ValueError):
        load_config({"APP_PORT": port})


@pytest.mark.parametrize("port", ["1", "65535"])
def test_port_bounds_accepted(port):
    assert load_config({"APP_PORT": port}).port == int(port)


def test_reads_os_environ_when_env_is_none(monkeypatch):
    monkeypatch.setenv("APP_PORT", "1234")
    monkeypatch.setenv("APP_DEBUG", "true")
    c = load_config()
    assert c.port == 1234 and c.debug is True


def test_main_unchanged():
    import main
    assert main.describe() == "serving on 127.0.0.1:8000"
