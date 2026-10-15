import pytest

from duration import parse_duration


@pytest.mark.parametrize("text,seconds", [("45s", 45), ("3m", 180), ("2h", 7200)])
def test_single_units(text, seconds):
    assert parse_duration(text) == seconds


def test_combined_units():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("2h5m10s") == 7510


@pytest.mark.parametrize("text", ["", "   ", "abc", "10", "5x", "1h30"])
def test_invalid_input_raises(text):
    with pytest.raises(ValueError):
        parse_duration(text)
