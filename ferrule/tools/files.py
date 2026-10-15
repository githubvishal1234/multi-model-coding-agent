"""read_file, search_repo, create_file, edit_file."""

import difflib
import fnmatch
import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

from ferrule.events import ApprovalRequest
from ferrule.safety import is_secret
from ferrule.tools import Tool, ToolContext, ToolResult

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache",
             ".pytest_cache", ".ruff_cache", "dist", "build"}
MAX_MATCHES = 200
PREVIEW_CHARS = 2000


def _read(path: Path) -> str:
    # newline="" keeps CRLF intact so edits don't rewrite every line ending.
    with open(path, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def _write(path: Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


class ReadFile(Tool):
    name = "read_file"
    description = "Read a text file in the workspace. Optional 1-based start_line and end_line."
    read_only = True

    class Args(BaseModel):
        path: str
        start_line: int | None = Field(None, ge=1)
        end_line: int | None = Field(None, ge=1)

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        p = ctx.resolve(a.path)
        if not p.is_file():
            return ToolResult(ok=False, error=f"not a file: {a.path}")
        lines = _read(p).splitlines(keepends=True)
        start = (a.start_line or 1) - 1
        end = a.end_line or len(lines)
        return ToolResult(ok=True, output="".join(lines[start:end]))


class SearchRepo(Tool):
    name = "search_repo"
    description = ("Search workspace files for text (or a regex if regex=true). "
                   "Returns path:line: text matches. glob filters files, e.g. '*.py'.")
    read_only = True

    class Args(BaseModel):
        pattern: str = Field(min_length=1)
        glob: str = "*"
        regex: bool = False

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        try:
            rx = re.compile(a.pattern if a.regex else re.escape(a.pattern))
        except re.error as e:
            return ToolResult(ok=False, error=f"bad regex: {e}")
        root = os.path.realpath(ctx.settings.workspace)
        hits = []
        for dirpath, dirnames, filenames in os.walk(root):  # does not follow symlinked dirs
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                rel = Path(os.path.relpath(full, root)).as_posix()
                if os.path.islink(full) or is_secret(fn):
                    continue
                if not (fnmatch.fnmatch(rel, a.glob) or fnmatch.fnmatch(fn, a.glob)):
                    continue
                try:
                    with open(full, "rb") as f:
                        data = f.read(2_000_000)
                except OSError:
                    continue
                if b"\0" in data[:1024]:  # binary
                    continue
                for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                    if rx.search(line):
                        hits.append(f"{rel}:{i}: {line.strip()[:200]}")
                        if len(hits) >= MAX_MATCHES:
                            hits.append(f"... [stopped at {MAX_MATCHES} matches]")
                            return ToolResult(ok=True, output="\n".join(hits))
        return ToolResult(ok=True, output="\n".join(hits) or "no matches")


class CreateFile(Tool):
    name = "create_file"
    description = "Create a new file with the given content. Fails if the file already exists."

    class Args(BaseModel):
        path: str = Field(min_length=1)
        content: str

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        p = ctx.resolve(a.path)
        if p.exists():
            return ToolResult(ok=False, error=f"{a.path} already exists; use edit_file")
        preview = a.content[:PREVIEW_CHARS]
        if len(a.content) > PREVIEW_CHARS:
            preview += "\n... [preview truncated]"
        req = ApprovalRequest("create_file", f"create {a.path} ({len(a.content)} chars)", preview)
        if not await ctx.approve(req):
            return ToolResult(ok=False, error="the user rejected creating this file")
        ctx.remember(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        _write(p, a.content)
        return ToolResult(ok=True, output=f"created {a.path}")


def _crlf(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\n", "\r\n")


class EditFile(Tool):
    name = "edit_file"
    description = ("Replace the exact text `old` with `new` in a file. `old` must appear exactly "
                   "once; copy it from read_file output including indentation.")

    class Args(BaseModel):
        path: str
        old: str = Field(min_length=1)
        new: str

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        p = ctx.resolve(a.path)
        if not p.is_file():
            return ToolResult(ok=False, error=f"not a file: {a.path}")
        text = _read(p)
        old, new = a.old, a.new
        if old not in text and "\r\n" in text:  # model wrote \n for a CRLF file
            old, new = _crlf(old), _crlf(new)
        count = text.count(old)
        if count != 1:
            return ToolResult(ok=False, error=(
                f"`old` text found {count} times in {a.path}; it must match exactly once. "
                "Read the file and copy the exact text."))
        updated = text.replace(old, new, 1)
        diff = "".join(difflib.unified_diff(
            text.splitlines(keepends=True), updated.splitlines(keepends=True),
            f"a/{a.path}", f"b/{a.path}"))
        if not await ctx.approve(ApprovalRequest("edit_file", f"edit {a.path}", diff)):
            return ToolResult(ok=False, error="the user rejected this edit")
        ctx.remember(p)
        _write(p, updated)
        return ToolResult(ok=True, output=f"edited {a.path}\n{diff}")
