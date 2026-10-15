import os
from dataclasses import dataclass, field

TRUE_VALUES = {"1", "true", "yes"}


@dataclass
class Config:
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    allowed_hosts: list[str] = field(default_factory=list)


def _port(raw):
    if not raw.strip().isdigit() or not 1 <= int(raw) <= 65535:
        raise ValueError(f"APP_PORT must be a whole number from 1 to 65535, got {raw!r}")
    return int(raw)


def load_config(env=None):
    env = os.environ if env is None else env
    return Config(
        host=env.get("APP_HOST", "127.0.0.1"),
        port=_port(env["APP_PORT"]) if "APP_PORT" in env else 8000,
        debug=env.get("APP_DEBUG", "").strip().lower() in TRUE_VALUES,
        allowed_hosts=[h.strip() for h in env.get("APP_ALLOWED_HOSTS", "").split(",") if h.strip()],
    )
