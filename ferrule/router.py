"""Task classifier and model router.

The router ranks models for a task class, skips ones that cannot be used (no API key, local-only
mode, too big for memory, measured too slow, provider cooling down, over its request caps),
falls back to the next model when a provider fails, and escalates to a stronger model when the
agent asks. Every decision is logged with its reason.
"""

import os
import re
import time
from collections import deque
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Literal

from ferrule.events import Event
from ferrule.providers import (
    BadResponse,
    OpenAICompatProvider,
    Provider,
    ProviderError,
    RateLimited,
    Reply,
    Unavailable,
)
from ferrule.registry import ModelSpec, ProviderSpec, Registry

TASK_CLASSES = ("boilerplate", "small_edit", "explain", "tests", "debug",
                "multi_file_refactor", "long_context")
LONG_CONTEXT_TOKENS = 16_000  # repository text above this is treated as long_context

# First match wins. Order matters: "test_x fails" is debugging, not writing tests.
RULES: list[tuple[str, re.Pattern]] = [(cls, re.compile(rx, re.IGNORECASE)) for cls, rx in (
    ("debug", r"traceback|\berror\b|exception|\bfails?\b|failing|\bbug\b|broken|crash"),
    ("tests", r"\btests?\b|pytest|unit test"),
    ("multi_file_refactor", r"\brename\b|refactor|everywhere|across .*files|\bmove\b.*\bto\b"),
    ("explain", r"\bexplain\b|what does|how does|\bwhich\b.*\?|answer"),
    ("boilerplate", r"\b(add|create|write)\b.*\b(route|endpoint|dataclass|dockerfile|workflow"
                    r"|option|flag|config|class|module|script)\b"),
)]
TEXT_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".rb", ".php", ".c",
                 ".h", ".cpp", ".cs", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".cfg"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}


def classify(task: str, repo_tokens: int = 0) -> str:
    if repo_tokens > LONG_CONTEXT_TOKENS:
        return "long_context"
    for cls, rx in RULES:
        if rx.search(task):
            return cls
    return "small_edit"


def estimate_repo_tokens(root: Path) -> int:
    """Rough size of the workspace's text files in tokens (about 4 characters per token)."""
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if Path(fn).suffix.lower() in TEXT_SUFFIXES:
                try:
                    total += os.path.getsize(os.path.join(dirpath, fn))
                except OSError:
                    pass
    return total // 4


class NoModelAvailable(ProviderError):
    pass


Profile = Literal["fast", "balanced", "quality"]


class Router:
    def __init__(self, registry: Registry, env: Mapping[str, str] | None = None, *,
                 local_only: bool = False, native_tools: bool = True,
                 profile: Profile = "balanced", installed: set[str] | None = None,
                 local_fit: set[str] | None = None, too_slow: set[str] = frozenset(),
                 max_hosted_requests: int = 50, cooldown_s: float = 60,
                 clock: Callable[[], float] = time.monotonic):
        self.registry = registry
        self.env = os.environ if env is None else env
        self.local_only = local_only
        self.native_tools = native_tools
        self.profile = profile
        self.installed = installed  # None = unknown, don't filter
        self.local_fit = local_fit  # None = unknown, don't filter
        self.too_slow = set(too_slow)
        self.max_hosted_requests = max_hosted_requests
        self.cooldown_s = cooldown_s
        self.clock = clock
        self.cooling: dict[str, float] = {}  # provider -> time it may be used again
        self.failed: set[str] = set()  # model names that returned a hard error
        self.minute: dict[str, deque] = {}  # provider -> request times in the last minute
        # ponytail: daily counts live in memory only (reset on restart); persist if caps matter.
        self.day: dict[str, int] = {}
        self.hosted_requests = 0

    def _skip_reason(self, m: ModelSpec, task_class: str, context_needed: int) -> str | None:
        p = self.registry.provider(m)
        if not p.available(self.env):
            return f"no API key ({p.api_key_env} not set)"
        if self.local_only and not p.local:
            return "local-only mode"
        if self.native_tools and not m.supports_tools:
            return "no native tool calling"
        if m.context < context_needed:
            return f"context {m.context} < {context_needed} needed"
        if p.local and self.installed is not None and m.name not in self.installed:
            return "not installed"
        if p.local and self.local_fit is not None and m.name not in self.local_fit:
            return "does not fit the memory budget"
        if m.name in self.too_slow:
            return "measured too slow"
        if m.name in self.failed:
            return "failed earlier in this session"
        if self.cooling.get(m.provider, 0) > self.clock():
            return f"{m.provider} cooling down after an error"
        cap = self._cap_reason(m.provider, p)
        return cap

    def _cap_reason(self, provider: str, p: ProviderSpec) -> str | None:
        if p.local:
            return None
        if self.hosted_requests >= self.max_hosted_requests:
            return f"session cap of {self.max_hosted_requests} hosted requests reached"
        now = self.clock()
        recent = self.minute.setdefault(provider, deque())
        while recent and now - recent[0] >= 60:
            recent.popleft()
        if p.caps.requests_per_minute and len(recent) >= p.caps.requests_per_minute:
            return f"{provider} per-minute cap reached"
        if p.caps.requests_per_day and self.day.get(provider, 0) >= p.caps.requests_per_day:
            return f"{provider} daily cap reached"
        return None

    def _sort_key(self, m: ModelSpec, task_class: str):
        score = m.scores.get(task_class, -1.0)  # measured models first, then by size
        size = m.params_b or 0.0
        local_first = 0 if self.registry.is_local(m) else 1
        if self.profile == "quality":
            return (-score, -size)
        if self.profile == "fast":
            return (local_first, size)
        return (local_first, -score, -size)  # balanced: free + private first, then hosted

    def ranked(self, task_class: str, context_needed: int = 0,
               exclude: set[str] = frozenset()) -> tuple[list[ModelSpec], dict[str, str]]:
        usable, skipped = [], {}
        for m in self.registry.models:
            reason = "already tried" if m.name in exclude else self._skip_reason(
                m, task_class, context_needed)
            if reason:
                skipped[m.name] = reason
            else:
                usable.append(m)
        return sorted(usable, key=lambda m: self._sort_key(m, task_class)), skipped

    def record_request(self, m: ModelSpec) -> None:
        if self.registry.is_local(m):
            return
        self.hosted_requests += 1
        self.minute.setdefault(m.provider, deque()).append(self.clock())
        self.day[m.provider] = self.day.get(m.provider, 0) + 1

    def cool_down(self, provider: str) -> None:
        self.cooling[provider] = self.clock() + self.cooldown_s

    def mark_failed(self, model: str) -> None:
        self.failed.add(model)


class RoutedProvider:
    """A Provider that asks the Router which model to use, and switches models on provider
    errors (fallback) or when the agent asks for a stronger one (escalate)."""

    def __init__(self, router: Router, task_class: str, *, context_needed: int = 0,
                 make_provider: Callable[[ModelSpec, ProviderSpec], Provider] | None = None,
                 redact: Callable[[str], str] = lambda s: s, timeout: float = 300,
                 params: dict | None = None):
        self.router = router
        self.task_class = task_class
        self.context_needed = context_needed
        self.redact = redact
        self.timeout = timeout
        self.params = params or {}
        self._make = make_provider or self._default_provider
        self._clients: dict[str, Provider] = {}
        self.current: ModelSpec | None = None
        self.tried: set[str] = set()
        self.notified: set[str] = set()
        self.emit: Callable[[Event], None] = lambda e: None
        self.audit = None

    def attach(self, emit, audit) -> None:
        self.emit, self.audit = emit, audit

    def _default_provider(self, m: ModelSpec, p: ProviderSpec) -> Provider:
        return OpenAICompatProvider(p.base_url, m.name, api_key=p.api_key(self.router.env),
                                    name=m.provider, is_local=p.local, timeout=self.timeout,
                                    params=self.params)

    def _client(self, m: ModelSpec) -> Provider:
        if m.name not in self._clients:
            self._clients[m.name] = self._make(m, self.router.registry.provider(m))
        return self._clients[m.name]

    def _log(self, kind: str, **data) -> None:
        self.emit(Event(kind, data))
        if self.audit:
            self.audit.write(kind, **data)

    def _select(self, reason: str) -> ModelSpec:
        ranked, skipped = self.router.ranked(self.task_class, self.context_needed, self.tried)
        if not ranked:
            details = "; ".join(f"{k}: {v}" for k, v in skipped.items())
            raise NoModelAvailable(f"no usable model for {self.task_class} ({details})")
        self.current = ranked[0]
        self._log("routing", task_class=self.task_class, chosen=self.current.name,
                  provider=self.current.provider, reason=reason,
                  candidates=[m.name for m in ranked], skipped=skipped)
        return self.current

    def _model(self) -> ModelSpec:
        return self.current or self._select("best available model")

    @property
    def model(self) -> str:
        return self._model().name

    @property
    def name(self) -> str:
        return self._model().provider

    @property
    def is_local(self) -> bool:
        return self.router.registry.is_local(self._model())

    def escalate(self, why: str) -> bool:
        """Switch to the next model in the ranking. False if there is nothing left to try."""
        if self.current is None:
            return False
        previous = self.current
        self.tried.add(previous.name)
        try:
            self._select(f"escalated from {previous.name}: {why}")
            return True
        except NoModelAvailable:
            self.tried.discard(previous.name)
            self.current = previous
            return False

    async def chat(self, messages, tools=None, on_token=None) -> Reply:
        while True:
            m = self._model()
            local = self.router.registry.is_local(m)
            cap = None if local else self.router._cap_reason(m.provider,
                                                             self.router.registry.provider(m))
            if cap:
                self.tried.add(m.name)
                self._select(f"{m.name} skipped: {cap}")
                continue
            if not local and m.provider not in self.notified:
                self.notified.add(m.provider)
                self._log("notice", message=f"sending code and prompts to {m.provider} "
                          f"({m.name}); the code leaves this machine")
            sent = messages if local else [
                {**msg, "content": self.redact(msg["content"])}
                if isinstance(msg.get("content"), str) else msg for msg in messages]
            self.router.record_request(m)
            try:
                return await self._client(m).chat(sent, tools, on_token)
            except (RateLimited, Unavailable) as e:
                self.router.cool_down(m.provider)
                why = f"{m.provider} {type(e).__name__}: {e}"
            except BadResponse as e:  # e.g. the model id no longer exists
                self.router.mark_failed(m.name)
                why = f"{m.name} error: {e}"
            self.tried.add(m.name)
            self._select(f"fallback after {why[:200]}")

    async def aclose(self) -> None:
        for client in self._clients.values():
            close = getattr(client, "aclose", None)
            if close:
                await close()


async def installed_models(base_url: str) -> set[str] | None:
    """Models Ollama has installed, or None if Ollama is not reachable."""
    from ferrule.providers import OllamaAdmin
    admin = OllamaAdmin(base_url, timeout=10)
    try:
        return await admin.installed()
    except Unavailable:
        return None
    finally:
        await admin.aclose()


async def build_provider(settings, task: str, extra_params: dict | None = None) -> Provider:
    """A fixed model if settings.model is set, otherwise a RoutedProvider over the registry,
    filtered by what is installed, what fits in memory and what was measured too slow."""
    from ferrule.hardware import detect, load_speeds, select_local
    from ferrule.registry import load_registry
    from ferrule.safety import Redactor

    params = {"max_tokens": settings.max_tokens, **(extra_params or {})}
    if settings.model:
        return OpenAICompatProvider(settings.base_url, settings.model,
                                    timeout=settings.model_timeout, params=params)
    registry = load_registry()
    installed = await installed_models(settings.base_url) or set()
    too_slow = {m for m, tps in load_speeds(settings.home).items()
                if tps < settings.min_tokens_per_sec}
    local = [m for m in registry.models if registry.is_local(m)]
    selection = select_local(local, detect(disk_path=settings.workspace), installed,
                             too_slow=too_slow)
    router = Router(registry, local_only=settings.local_only,
                    native_tools=settings.supports_tools, profile=settings.profile,
                    installed=installed, local_fit=set(selection.fitting), too_slow=too_slow,
                    max_hosted_requests=settings.max_hosted_requests)
    task_class = classify(task, estimate_repo_tokens(settings.workspace))
    return RoutedProvider(router, task_class, redact=Redactor(), timeout=settings.model_timeout,
                          params=params)
