from app import handle


def test_health():
    assert handle("/health") == (200, {"status": "ok"})


def test_unknown_route():
    assert handle("/nope")[0] == 404
