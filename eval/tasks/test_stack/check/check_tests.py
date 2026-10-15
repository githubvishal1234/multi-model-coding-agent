"""Pass if test_stack.py passes on the real Stack and fails on each broken version."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ORIGINAL = 'class Stack:\n    """Last-in, first-out stack."""\n\n    def __init__(self):\n        self._items = []\n\n    def push(self, item):\n        self._items.append(item)\n\n    def pop(self):\n        """Remove and return the top item. Raises IndexError if the stack is empty."""\n        if not self._items:\n            raise IndexError("pop from empty stack")\n        return self._items.pop()\n\n    def peek(self):\n        """Return the top item without removing it. Raises IndexError if the stack is empty."""\n        if not self._items:\n            raise IndexError("peek at empty stack")\n        return self._items[-1]\n\n    def is_empty(self):\n        return not self._items\n\n    def __len__(self):\n        return len(self._items)\n'

BROKEN = {
    "pops from the bottom": ORIGINAL.replace("return self._items.pop()", "return self._items.pop(0)"),
    "removes the item on peek": ORIGINAL.replace("return self._items[-1]", "return self._items.pop()"),
    "returns None when popping empty": ORIGINAL.replace(
        'raise IndexError("pop from empty stack")', "return None"),
    "returns None when peeking empty": ORIGINAL.replace(
        'raise IndexError("peek at empty stack")', "return None"),
    "has is_empty inverted": ORIGINAL.replace("return not self._items", "return bool(self._items)"),
    "miscounts len after pops": ORIGINAL.replace(
        "        self._items.append(item)\n",
        "        self._items.append(item)\n        self.pushed = getattr(self, 'pushed', 0) + 1\n"
    ).replace("return len(self._items)", "return getattr(self, 'pushed', 0)"),
}
assert all(code != ORIGINAL for code in BROKEN.values())


def pytest(cwd):
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_stack.py"]
    return subprocess.run(cmd, cwd=cwd, capture_output=True).returncode


test_file = pathlib.Path("test_stack.py")
if not test_file.exists():
    sys.exit("FAIL: test_stack.py was not created")
with tempfile.TemporaryDirectory() as tmp:  # run against the original, even if it was edited
    shutil.copy(test_file, tmp)
    pathlib.Path(tmp, "stack.py").write_text(ORIGINAL)
    if pytest(tmp) != 0:
        sys.exit("FAIL: the tests fail on the correct Stack")
for name, code in BROKEN.items():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(test_file, tmp)
        pathlib.Path(tmp, "stack.py").write_text(code)
        if pytest(tmp) == 0:
            sys.exit(f"FAIL: the tests did not catch a Stack that {name}")
print("ok")
