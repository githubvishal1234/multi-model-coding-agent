"""Pass if ANSWER.md names the real loader, env var and default, and the code still works."""
import os
import pathlib
import sys

answer_file = pathlib.Path("ANSWER.md")
if not answer_file.exists():
    sys.exit("FAIL: ANSWER.md was not created")
answer = answer_file.read_text(encoding="utf-8", errors="replace")
for fact in ("load_database_url", "APP_DATABASE_URL", "sqlite:///data/app.db"):
    if fact not in answer:
        sys.exit(f"FAIL: ANSWER.md does not mention {fact}")

os.environ.pop("APP_DATABASE_URL", None)
sys.path.insert(0, ".")
from app.main import start  # noqa: E402

if start() != "[INFO] connected to sqlite:///data/app.db":
    sys.exit("FAIL: the code was changed")
print("ok")
