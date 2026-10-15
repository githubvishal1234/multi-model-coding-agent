"""Task format and loader.

A task is a directory with task.yaml:

    id: fix_median                # unique
    class: debug                  # router task class
    instruction: "..."            # what the agent is asked to do
    repo: repo                    # starting snapshot, copied fresh for every run
    test_command: [...]           # optional; what the agent's run_tests runs
    check:
      command: ["{python}", "-m", "pytest", "-q"]   # {python} = the harness's interpreter
      expect_exit: 0
      files: check                # optional hidden files copied in only for the check
    solution: solution            # optional reference files; used by --agent reference
    max_steps: 40                 # optional; overrides the config for tasks that need more

Paths are relative to the task directory.
"""

import glob
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

TaskClass = Literal["boilerplate", "small_edit", "explain", "tests", "debug",
                    "multi_file_refactor", "long_context"]
DEFAULT_TEST_COMMAND = ["{python}", "-m", "pytest", "-q", "-p", "no:cacheprovider"]


class Check(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command: list[str] = Field(min_length=1)
    expect_exit: int = 0
    files: str | None = None


class Task(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    id: str = Field(pattern=r"^[a-z0-9_]+$")
    task_class: TaskClass = Field(alias="class")
    instruction: str = Field(min_length=1)
    repo: str = "repo"
    test_command: list[str] = Field(default_factory=lambda: list(DEFAULT_TEST_COMMAND))
    check: Check
    solution: str | None = None
    max_steps: int | None = Field(None, ge=1)
    dir: Path = Field(default=Path("."), exclude=True)

    def path(self, rel: str) -> Path:
        return self.dir / rel


def load_task(path: Path) -> Task:
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        task = Task.model_validate({**(data or {}), "dir": path.parent})
    except (yaml.YAMLError, ValidationError) as e:
        raise ValueError(f"{path}: invalid task file:\n{e}") from None
    for rel in (task.repo, task.check.files, task.solution):
        if rel is not None and not task.path(rel).is_dir():
            raise ValueError(f"{path}: directory not found: {rel}")
    return task


def load_tasks(patterns: list[str], base: Path) -> list[Task]:
    """Load every task.yaml matched by the glob patterns (relative to base), sorted by id."""
    files = sorted({Path(f) for p in patterns for f in glob.glob(str(base / p))})
    tasks = sorted((load_task(f) for f in files), key=lambda t: t.id)
    ids = [t.id for t in tasks]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"duplicate task ids: {', '.join(dupes)}")
    if not tasks:
        raise ValueError(f"no tasks matched {patterns} under {base}")
    return tasks
