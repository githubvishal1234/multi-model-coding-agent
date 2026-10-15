"""Pass if test_duration.py passes on the real parser and fails on each broken version."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ORIGINAL = 'import re\n\n_PART = re.compile(r"(\\d+)([hms])")\n_SECONDS = {"h": 3600, "m": 60, "s": 1}\n\n\ndef parse_duration(text):\n    """Parse a duration like "1h30m", "45s" or "2h5m10s" into seconds.\n\n    Raises ValueError for empty or malformed input.\n    """\n    text = text.strip()\n    if not text or _PART.sub("", text):\n        raise ValueError(f"invalid duration: {text!r}")\n    return sum(int(n) * _SECONDS[unit] for n, unit in _PART.findall(text))\n'

BROKEN = {
    "ignores seconds": ORIGINAL.replace('"s": 1', '"s": 0'),
    "treats hours as minutes": ORIGINAL.replace('"h": 3600', '"h": 60'),
    "treats minutes as hours": ORIGINAL.replace('"m": 60', '"m": 3600'),
    "accepts invalid input": ORIGINAL.replace(
        'raise ValueError(f"invalid duration: {text!r}")', "return 0"),
}
assert all(code != ORIGINAL for code in BROKEN.values())


def pytest(cwd):
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_duration.py"]
    return subprocess.run(cmd, cwd=cwd, capture_output=True).returncode


test_file = pathlib.Path("test_duration.py")
if not test_file.exists():
    sys.exit("FAIL: test_duration.py was not created")
with tempfile.TemporaryDirectory() as tmp:  # run against the original, even if it was edited
    shutil.copy(test_file, tmp)
    pathlib.Path(tmp, "duration.py").write_text(ORIGINAL)
    if pytest(tmp) != 0:
        sys.exit("FAIL: the tests fail on the correct parse_duration")
for name, code in BROKEN.items():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(test_file, tmp)
        pathlib.Path(tmp, "duration.py").write_text(code)
        if pytest(tmp) == 0:
            sys.exit(f"FAIL: the tests did not catch a parse_duration that {name}")
print("ok")
