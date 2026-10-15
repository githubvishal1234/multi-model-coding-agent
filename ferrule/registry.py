"""Model registry: providers and models from models.yaml. Keys come from env vars only."""

import os
from collections.abc import Mapping
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

DEFAULT_REGISTRY = Path(__file__).with_name("models.yaml")


class Caps(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requests_per_minute: int | None = Field(None, ge=1)
    requests_per_day: int | None = Field(None, ge=1)


class ProviderSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    base_url: str
    local: bool = False
    api_key_env: str | None = None  # the NAME of the env var, never the key
    caps: Caps = Field(default_factory=Caps)

    def api_key(self, env: Mapping[str, str]) -> str | None:
        return env.get(self.api_key_env) if self.api_key_env else None

    def available(self, env: Mapping[str, str]) -> bool:
        """Local providers always; hosted ones only when their key is set."""
        return self.local or bool(self.api_key(env))


class ModelSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    provider: str
    params_b: float | None = None
    context: int = Field(8192, ge=512)
    supports_tools: bool = False
    scores: dict[str, float] = Field(default_factory=dict)  # set by the eval harness only


class Registry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    providers: dict[str, ProviderSpec]
    models: list[ModelSpec]

    @model_validator(mode="after")
    def _check_references(self):
        unknown = sorted({m.provider for m in self.models} - self.providers.keys())
        if unknown:
            raise ValueError(f"models refer to unknown providers: {', '.join(unknown)}")
        return self

    def provider(self, model: ModelSpec) -> ProviderSpec:
        return self.providers[model.provider]

    def is_local(self, model: ModelSpec) -> bool:
        return self.provider(model).local


def load_registry(path: Path | None = None, env: Mapping[str, str] | None = None) -> Registry:
    env = os.environ if env is None else env
    path = Path(path or env.get("FERRULE_REGISTRY") or DEFAULT_REGISTRY)
    try:
        return Registry.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
    except (yaml.YAMLError, ValidationError, ValueError) as e:
        raise ValueError(f"{path}: invalid registry:\n{e}") from None
