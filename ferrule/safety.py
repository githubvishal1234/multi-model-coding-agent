"""Workspace confinement, secret-file denial, command allowlist, redaction, SQL read-only check,
private database values and audit log."""

import fnmatch
import json
import os
import re
import time
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit


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
DB_ENV_PREFIX = "FERRULE_DB_"  # FERRULE_DB_<NAME>=<connection URL>
DB_PASSWORD_RE = re.compile(r"(?:PWD|password)=([^;&]+)", re.IGNORECASE)  # in odbc_connect=...


def _db_secrets(url: str) -> set[str]:
    """The whole connection URL and any password inside it."""
    found = {url, *DB_PASSWORD_RE.findall(url)}
    try:
        found.add(urlsplit(url).password or "")
    except ValueError:
        pass
    return {s for s in found if len(s) >= 4}


class Redactor:
    """Replaces known key formats, the values of secret-looking env vars and database
    connection URLs and passwords with [REDACTED]."""

    def __init__(self, env: Mapping[str, str] | None = None):
        env = os.environ if env is None else env
        values = {v for k, v in env.items()
                  if len(v) >= 8 and any(h in k.upper() for h in SECRET_ENV_HINTS)}
        for k, v in env.items():
            if k.upper().startswith(DB_ENV_PREFIX) and "://" in v:
                values |= _db_secrets(v)
        self.values = sorted(values, key=len, reverse=True)

    def __call__(self, text: str) -> str:
        for value in self.values:
            text = text.replace(value, "[REDACTED]")
        for rx in SECRET_RES:
            text = rx.sub("[REDACTED]", text)
        return text


# --- database rows: never sent to hosted models ---
# Tools wrap row values (and database errors, which can quote them) in these markers.
# RoutedProvider replaces marked text before any message goes to a hosted provider.
PRIVATE_START = "<<ferrule-private:"
PRIVATE_END = "<<ferrule-private-end>>"
# No end marker = cut off by output truncation: withhold to the end of the text.
PRIVATE_RE = re.compile(re.escape(PRIVATE_START) + r"([^>]*)>>.*?(?:" + re.escape(PRIVATE_END)
                        + r"|\Z)", re.DOTALL)


def mark_private(text: str, label: str) -> str:
    return f"{PRIVATE_START}{label}>>\n{text}\n{PRIVATE_END}"


def withhold_private(text: str) -> str:
    return PRIVATE_RE.sub(lambda m: f"[{m.group(1)} withheld: database values are only sent "
                                    "to local models]", text)


# --- SQL: which statements may run on a read-only connection ---
# Comments, string literals and quoted identifiers are removed before the keyword checks.
SQL_STRIP_RE = re.compile(r"--[^\n]*|/\*.*?\*/|'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"|\[[^\]]*\]"
                          r"|`[^`]*`", re.DOTALL)
# Writes, batches and side-effecting functions that can follow SELECT/WITH. Over-blocking is
# fine: a blocked read is routed to the write path, which needs a writable connection.
SQL_WRITE_RE = re.compile(
    r"\b(insert|update|delete|merge|upsert|drop|alter|create|truncate|grant|revoke|deny|exec"
    r"|execute|call|into|backup|restore|dbcc|kill|shutdown|bulk|openrowset|opendatasource"
    r"|openquery|waitfor|reconfigure|set|use|declare|copy|lock|vacuum|attach|detach|pragma"
    r"|rename|sleep|benchmark|load_file|get_lock|nextval|setval|set_config|dblink\w*"
    r"|pg_\w+|lo_\w+|xp_\w+|sp_\w+)\b", re.IGNORECASE)


def is_read_only_sql(sql: str) -> bool:
    """True only for a single SELECT or WITH query with no write keyword.

    ponytail: keyword check, not a SQL parser. A user-defined function with side effects
    still passes; reads also run in a transaction that is rolled back. For real protection
    give read-only connections a database login that can only read (e.g. db_datareader).
    """
    s = SQL_STRIP_RE.sub(" ", sql).strip().rstrip(";").strip()
    if not s or ";" in s:  # empty, or more than one statement
        return False
    return s.split(None, 1)[0].lower() in ("select", "with") and not SQL_WRITE_RE.search(s)


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
