"""Workspace confinement, secret-file denial, command allowlist, redaction and audit log."""

import fnmatch
import json
import os
import re
import time
from collections.abc import Mapping
from pathlib import Path


class SafetyError(Exception):
    """An action was refused by the safety layer."""


SECRET_PATTERNS = (
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "id_dsa*", "id_ecdsa*",
    "id_ed25519*", "*credentials*", ".netrc", ".npmrc", ".pypirc",
)
SECRET_ALLOWED = (".env.example", ".env.sample", ".env.template")


def is_secret(path: str | Path) -> bool:
    name = Path(path).name.lower()
    return name not in SECRET_ALLOWED and any(fnmatch.fnmatch(name, p) for p in SECRET_PATTERNS)


def resolve(root: str | Path, path: str | Path) -> Path:
    """Return the real path of `path` inside `root`, or raise SafetyError.

    realpath follows `..`, symlinks and Windows junctions before the check, so none of them
    can point outside the workspace. An absolute `path` replaces root in join() and is checked
    the same way.
    """
    root_real = os.path.realpath(root)
    target = os.path.realpath(os.path.join(root_real, path))
    try:
        inside = os.path.commonpath([os.path.normcase(root_real), os.path.normcase(target)])
        inside = inside == os.path.normcase(root_real)
    except ValueError:  # different drives on Windows
        inside = False
    if not inside:
        raise SafetyError(f"path is outside the workspace: {path}")
    # lower(): `.GIT` is the same directory on case-insensitive filesystems (Windows, macOS)
    if ".git" in (p.lower() for p in Path(os.path.relpath(target, root_real)).parts):
        raise SafetyError(f"access to .git is not allowed: {path}")
    if is_secret(target):
        raise SafetyError(f"secret file is not readable or writable: {path}")
    return Path(target)


SHELL_CHARS = set("&|;<>`$\r\n")


def check_command(argv: list[str], allowlist: Mapping[str, list[str] | None]) -> str:
    """Validate argv against the allowlist; return the normalized program name."""
    if not argv:
        raise SafetyError("empty command")
    if Path(argv[0]).name != argv[0]:
        raise SafetyError(f"use a bare program name, not a path: {argv[0]}")
    prog = argv[0].lower()
    for ext in (".exe", ".cmd", ".bat"):
        prog = prog.removesuffix(ext)
    if prog not in allowlist:
        allowed_progs = ", ".join(sorted(allowlist))
        raise SafetyError(f"'{prog}' is not on the command allowlist: {allowed_progs}")
    allowed = allowlist[prog]
    if allowed is not None and (len(argv) < 2 or argv[1] not in allowed):
        raise SafetyError(f"'{prog}' only allows: {', '.join(allowed)}")
    if any(SHELL_CHARS & set(arg) for arg in argv):
        raise SafetyError("shell metacharacters are not allowed in arguments")
    return prog


SECRET_RES = [re.compile(p) for p in (
    r"sk-[A-Za-z0-9_\-]{16,}",
    r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"xox[abprs]-[A-Za-z0-9\-]{10,}",
    r"AIza[0-9A-Za-z_\-]{35}",
    r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
)]
SECRET_ENV_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD")


class Redactor:
    """Replaces known key formats and the values of secret-looking env vars with [REDACTED]."""

    def __init__(self, env: Mapping[str, str] | None = None):
        env = os.environ if env is None else env
        values = {v for k, v in env.items()
                  if len(v) >= 8 and any(h in k.upper() for h in SECRET_ENV_HINTS)}
        self.values = sorted(values, key=len, reverse=True)

    def __call__(self, text: str) -> str:
        for value in self.values:
            text = text.replace(value, "[REDACTED]")
        for rx in SECRET_RES:
            text = rx.sub("[REDACTED]", text)
        return text


class AuditLog:
    """Append-only JSON-lines log; every line is redacted before it is written."""

    def __init__(self, path: Path, redact: Redactor):
        self.path = Path(path)
        self.redact = redact
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: str, **fields) -> None:
        record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "event": event, **fields}
        line = self.redact(json.dumps(record, default=str))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
