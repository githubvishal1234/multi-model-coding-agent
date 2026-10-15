import re

_PART = re.compile(r"(\d+)([hms])")
_SECONDS = {"h": 3600, "m": 60, "s": 1}


def parse_duration(text):
    """Parse a duration like "1h30m", "45s" or "2h5m10s" into seconds.

    Raises ValueError for empty or malformed input.
    """
    text = text.strip()
    if not text or _PART.sub("", text):
        raise ValueError(f"invalid duration: {text!r}")
    return sum(int(n) * _SECONDS[unit] for n, unit in _PART.findall(text))
