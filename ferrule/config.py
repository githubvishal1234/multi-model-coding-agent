"""Settings: defaults, overridden by FERRULE_* environment variables, overridden by CLI flags."""

import json
import os
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Literal, get_origin

from pydantic import BaseModel, Field

# program -> allowed first argument (None = any). Every command still needs approval.
DEFAULT_ALLOWLIST: dict[str, list[str] | None] = {
    "python": ["-m"],
    "pytest": None,
    "ruff": ["check", "format"],
    "git": ["status", "diff", "log", "show"],
    "npm": ["test", "run"],
}


def load_dotenv(path: Path, environ: MutableMapping[str, str] | None = None) -> list[str]:
    """Read KEY=VALUE lines from a .env file into the environment. Variables that are already
    set win. Blank lines, # comments, `export ` prefixes and surrounding quotes are handled.
    Returns the names loaded (never the values)."""
    environ = os.environ if environ is None else environ
    try:
        lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return []
    loaded = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        elif " #" in value:  # trailing comment on an unquoted value
            value = value.split(" #", 1)[0].rstrip()
        if key and value and key not in environ:
            environ[key] = value
            loaded.append(key)
    return loaded


class Settings(BaseModel):
    workspace: Path = Field(default_factory=Path.cwd)
    home: Path = Field(default_factory=lambda: Path.home() / ".ferrule")
    base_url: str = "http://127.0.0.1:11434/v1"
    model: str | None = None  # a fixed Ollama model; None = let the router choose
    supports_tools: bool = True
    local_only: bool = False  # never send code to hosted providers
    profile: Literal["fast", "balanced", "quality"] = "balanced"
    max_hosted_requests: int = Field(50, ge=0)  # per run
    min_tokens_per_sec: float = Field(4.0, gt=0)  # starting guess; tune after `ferrule doctor`
    max_steps: int = Field(20, ge=1)
    max_invalid: int = Field(3, ge=0)
    model_timeout: float = Field(300, gt=0)
    command_timeout: float = Field(120, gt=0)
    max_output_chars: int = Field(8000, ge=200)
    max_tokens: int = Field(4096, ge=256)  # per model reply; stops runaway repetition early
    approval: Literal["ask", "auto_safe"] = "ask"
    allowlist: dict[str, list[str] | None] = Field(default_factory=lambda: dict(DEFAULT_ALLOWLIST))
    test_command: list[str] = Field(default_factory=lambda: ["python", "-m", "pytest", "-q"])

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None, **overrides) -> "Settings":
        env = os.environ if env is None else env
        data = {}
        for name, field in cls.model_fields.items():
            raw = env.get(f"FERRULE_{name.upper()}")
            if raw is not None:
                is_json = get_origin(field.annotation) in (list, dict)
                data[name] = json.loads(raw) if is_json else raw
        data.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**data)
