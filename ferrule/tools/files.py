"""read_file, search_repo, write_file, edit_file."""

import difflib
import fnmatch
import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

from ferrule.events import ApprovalRequest
from ferrule.safety import is_secret, mark_private
from ferrule.tools import Tool, ToolContext, ToolResult

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".mypy_cache",
             ".pytest_cache", ".ruff_cache", "dist", "build"}
MAX_MATCHES = 200
SEARCH_BYTES = 2_000_000  # per file
MAX_READ_BYTES = 50_000_000  # read_file refuses bigger files
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
        size = p.stat().st_size
        if size > MAX_READ_BYTES:  # reading it would take ~3-8x its size in memory for 8 KB
            return ToolResult(ok=False, error=(
                f"{a.path} is {size / 1e6:.0f} MB; read_file only reads files up to "
                f"{MAX_READ_BYTES // 1_000_000} MB. For data files use load_csv and run_sql, "
                "or a small python -m script that streams the file."))
        lines = _read(p).splitlines(keepends=True)
        start = (a.start_line or 1) - 1
        end = a.end_line or len(lines)
        text = "".join(lines[start:end])
        if private_data(ctx, p):
            text = mark_private(text, f"contents of {a.path}")
        return ToolResult(ok=True, output=text)


def private_data(ctx: ToolContext, path) -> bool:
    """Data files (settings.private_files) are kept from hosted models while database values
    are private. `path` may be absolute or workspace-relative."""
    s = ctx.settings
    if not s.databases or s.db_rows_to_hosted:
        return False
    p = Path(path)
    rel = Path(os.path.relpath(p, s.workspace)).as_posix() if p.is_absolute() else p.as_posix()
    name = p.name.lower()
    return any(fnmatch.fnmatch(name, g.lower()) or fnmatch.fnmatch(rel.lower(), g.lower())
               for g in s.private_files)


def workspace_files(root, glob: str = "*"):
    """Yield (relative posix path, full path) for workspace files, skipping SKIP_DIRS,
    symlinks and secret files. Does not follow symlinked directories."""
    root = os.path.realpath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = Path(os.path.relpath(full, root)).as_posix()
            if os.path.islink(full) or is_secret(fn):
                continue
            if fnmatch.fnmatch(rel, glob) or fnmatch.fnmatch(fn, glob):
                yield rel, full


def list_files_text(root, glob: str = "*", limit: int = MAX_MATCHES) -> str:
    paths = []
    for rel, _ in workspace_files(root, glob):
        if len(paths) >= limit:
            paths.append(f"... [stopped at {limit} files; use a narrower glob]")
            break
        paths.append(rel)
    return "\n".join(paths) or "no files"


class ListFiles(Tool):
    name = "list_files"
    description = "List workspace file paths. glob filters them, e.g. '*.py' or 'src/*'."
    read_only = True

    class Args(BaseModel):
        glob: str = "*"

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        return ToolResult(ok=True, output=list_files_text(ctx.settings.workspace, a.glob))


class SearchRepo(Tool):
    name = "search_repo"
    description = ("Search workspace files for text (or a regex if regex=true). "
                   "Returns path:line: text matches, and paths whose name matches. "
                   "glob filters files, e.g. '*.py'.")
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
        hits, private, partial = [], [], []
        for rel, full in workspace_files(ctx.settings.workspace, a.glob):
            # Seen in eval: models search for "app.py" to find a file, which never matched text.
            if rx.search(rel):
                hits.append(f"{rel}: [file name matches]")
            if private_data(ctx, rel):
                private.append(rel)  # contents are private data: never returned as hits
                continue
            try:
                with open(full, "rb") as f:
                    data = f.read(SEARCH_BYTES + 1)
            except OSError:
                continue
            if b"\0" in data[:1024]:  # binary
                continue
            if len(data) > SEARCH_BYTES:
                data = data[:SEARCH_BYTES]
                partial.append(rel)
            for i, line in enumerate(data.decode("utf-8", "replace").splitlines(), 1):
                if rx.search(line):
                    hits.append(f"{rel}:{i}: {line.strip()[:200]}")
            if len(hits) >= MAX_MATCHES:
                hits = hits[:MAX_MATCHES] + [f"... [stopped at {MAX_MATCHES} matches]"]
                break
        # Notes go first: run_tool cuts long output at the end, and a silent "no matches" for
        # text that was never searched misled models in tests.
        notes = []
        if private:
            notes.append(f"[not searched: the contents of {len(private)} private data files, "
                         f"e.g. {private[0]}; use load_csv + run_sql for data]")
        if partial:
            notes.append(f"[only the first {SEARCH_BYTES // 1_000_000} MB was searched in "
                         f"{len(partial)} files, e.g. {partial[0]}]")
        return ToolResult(ok=True, output="\n".join(notes + (hits or ["no matches"])))


def _crlf(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\n", "\r\n")


class WriteFile(Tool):
    """Whole-file writes suit small models: they write complete files far more reliably than
    exact search/replace edits (eval transcripts: broken indentation, failed matches)."""

    name = "write_file"
    description = ("Create a file, or replace a whole file, with its complete new content. "
                   "Best for new files and small files. Always write the entire file, "
                   "never a fragment.")

    class Args(BaseModel):
        path: str = Field(min_length=1)
        content: str

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        p = ctx.resolve(a.path)
        if p.is_dir():
            return ToolResult(ok=False, error=f"{a.path} is a directory")
        if not p.exists():
            preview = a.content[:PREVIEW_CHARS]
            if len(a.content) > PREVIEW_CHARS:
                preview += "\n... [preview truncated]"
            summary, detail = f"create {a.path} ({len(a.content)} chars)", preview
            content = a.content
        else:
            old = _read(p)
            content = _crlf(a.content) if "\r\n" in old else a.content  # keep line endings
            if content == old:
                return ToolResult(ok=True, output=f"{a.path} already has this content")
            detail = "".join(difflib.unified_diff(
                old.splitlines(keepends=True), content.splitlines(keepends=True),
                f"a/{a.path}", f"b/{a.path}"))
            summary = f"replace {a.path}"
        if not await ctx.approve(ApprovalRequest("write_file", summary, detail)):
            return ToolResult(ok=False, error=f"the user rejected this change ({summary})")
        ctx.remember(p)
        p.parent.mkdir(parents=True, exist_ok=True)
        _write(p, content)
        verb = "created" if summary.startswith("create") else "replaced"
        return ToolResult(ok=True, output=f"{verb} {a.path}")


class EditFile(Tool):
    name = "edit_file"
    description = ("Replace the exact text `old` with `new` in an existing file. `old` must "
                   "appear exactly once; copy it from read_file output including indentation. "
                   "To create a file or rewrite a small file, use write_file instead.")

    class Args(BaseModel):
        path: str
        old: str = Field(min_length=1)
        new: str

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        p = ctx.resolve(a.path)
        if not p.is_file():
            return ToolResult(ok=False, error=f"not a file: {a.path}. Use write_file to create it.")
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
