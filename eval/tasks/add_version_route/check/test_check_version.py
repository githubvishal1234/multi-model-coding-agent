from app import handle
from version import __version__


def test_version_route():
    assert handle("/version") == (200, {"version": __version__})


def test_health_still_works():
    assert handle("/health") == (200, {"status": "ok"})
