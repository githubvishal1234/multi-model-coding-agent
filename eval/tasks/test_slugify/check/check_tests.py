"""Pass if test_text.py passes on the real slugify and fails on broken versions."""
import pathlib
import shutil
import subprocess
import sys
import tempfile


def pytest(cwd):
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_text.py"]
    return subprocess.run(cmd, cwd=cwd, capture_output=True).returncode


BROKEN = {
    "keeps punctuation": 'def slugify(title):\n    return "-".join(title.lower().split())\n',
    "keeps capitals": 'import re\n\ndef slugify(title):\n'
                      '    return "-".join(re.findall(r"[A-Za-z0-9]+", title))\n',
    "keeps extra spaces": 'import re\n\ndef slugify(title):\n'
                          '    return re.sub(r"[^a-z0-9 ]", "", title.lower()).replace(" ", "-")\n',
}

test_file = pathlib.Path("test_text.py")
if not test_file.exists():
    sys.exit("FAIL: test_text.py was not created")
if test_file.read_text().count("def test_") < 2:
    sys.exit("FAIL: need at least two test functions")
if pytest(".") != 0:
    sys.exit("FAIL: the tests fail on the correct slugify")
for name, code in BROKEN.items():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(test_file, tmp)
        pathlib.Path(tmp, "text.py").write_text(code)
        if pytest(tmp) == 0:
            sys.exit(f"FAIL: the tests did not catch a slugify that {name}")
print("ok")
