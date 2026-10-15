"""Undo the last run: restore each file to the snapshot taken before its first change.

Snapshots (not git refs) so untracked files and non-git folders can be undone too.
"""

import hashlib
import json
import os
from pathlib import Path

from ferrule import safety
from ferrule.config import Settings


def _checkpoint_path(settings: Settings) -> Path:
    ws = os.path.normcase(os.path.realpath(settings.workspace))
    return settings.home / "checkpoints" / f"{hashlib.sha256(ws.encode()).hexdigest()[:16]}.json"


def save_checkpoint(settings: Settings, originals: dict[str, str | None]) -> None:
    path = _checkpoint_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"workspace": str(settings.workspace), "files": originals}),
                    encoding="utf-8")


def undo(settings: Settings) -> list[str]:
    """Restore files changed by the last run; return their paths. Empty if nothing to undo."""
    path = _checkpoint_path(settings)
    if not path.exists():
        return []
    files = json.loads(path.read_text(encoding="utf-8"))["files"]
    for file, content in files.items():
        target = safety.resolve(settings.workspace, file)  # re-check: the checkpoint is on disk
        if content is None:
            target.unlink(missing_ok=True)
        else:
            with open(target, "w", encoding="utf-8", newline="") as f:
                f.write(content)
    path.unlink()
    return list(files)
