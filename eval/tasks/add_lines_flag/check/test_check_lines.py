import subprocess
import sys

import pytest

SAMPLE = "a b c\nd e\n\nf"  # 6 words, 4 lines, only 3 newline characters


def run(tmp_path, *flags):
    f = tmp_path / "sample.txt"
    f.write_bytes(SAMPLE.encode())
    cmd = [sys.executable, "wordcount.py", str(f), *flags]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


def test_default_output_unchanged(tmp_path):
    assert run(tmp_path) == "6 words\n"


@pytest.mark.parametrize("flag", ["--lines", "-l"])
def test_lines_flag(tmp_path, flag):
    assert run(tmp_path, flag) == "6 words\n4 lines\n"


def test_help_mentions_option():
    out = subprocess.run([sys.executable, "wordcount.py", "--help"],
                         capture_output=True, text=True).stdout
    assert "--lines" in out and "-l" in out
