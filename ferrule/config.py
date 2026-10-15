"""Settings: defaults, overridden by FERRULE_* environment variables, overridden by CLI flags."""

import json
import os
from collections.abc import Mapping
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


class Settings(BaseModel):
    workspace: Path = Field(default_factory=Path.cwd)
    home: Path = Field(default_factory=lambda: Path.home() / ".ferrule")
    base_url: str = "http://127.0.0.1:11434/v1"
    model: str = "qwen2.5-coder:7b"
    supports_tools: bool = True
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
