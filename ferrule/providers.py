"""Model providers. One OpenAI-compatible chat client serves Ollama (/v1) and hosted tiers."""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

import httpx


class ProviderError(Exception):
    pass


class RateLimited(ProviderError):
    """HTTP 429. The router falls back to another provider."""


class Unavailable(ProviderError):
    """Connection refused, timeout or 5xx. The router falls back to another provider."""


class BadResponse(ProviderError):
    """Other 4xx or an unparseable stream."""


@dataclass
class Reply:
    content: str = ""
    tool_calls: list[dict] = field(default_factory=list)  # OpenAI format
    usage: dict = field(default_factory=dict)


class Provider(Protocol):
    name: str
    model: str
    is_local: bool

    async def chat(self, messages: list[dict], tools: list[dict] | None = None,
                   on_token: Callable[[str], None] | None = None) -> Reply: ...


def _status_error(code: int, detail: str) -> ProviderError:
    if code == 429:
        return RateLimited(f"rate limited: {detail}")
    if code >= 500:
        return Unavailable(f"server error {code}: {detail}")
    return BadResponse(f"HTTP {code}: {detail}")


class OpenAICompatProvider:
    def __init__(self, base_url: str, model: str, *, api_key: str | None = None,
                 name: str = "ollama", is_local: bool = True, timeout: float = 300,
                 client: httpx.AsyncClient | None = None, params: dict | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.name = name
        self.is_local = is_local
        self.params = params or {}  # extra request fields, e.g. temperature/seed for eval runs
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = client or httpx.AsyncClient(timeout=timeout)

    def __repr__(self) -> str:  # never show the key
        return f"OpenAICompatProvider(name={self.name!r}, model={self.model!r})"

    async def aclose(self) -> None:
        await self._client.aclose()

    async def available_models(self) -> set[str]:
        """Model ids the provider serves right now (GET /models). Free-tier ids change often."""
        try:
            resp = await self._client.get(f"{self.base_url}/models", headers=self._headers)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise Unavailable(f"{self.name}: {type(e).__name__}: {e}") from e
        if resp.status_code != 200:
            raise _status_error(resp.status_code, resp.text[:300])
        # Some providers prefix ids (e.g. "models/gemini-..."); keep both forms.
        ids = {m.get("id", "") for m in resp.json().get("data", [])}
        return ids | {i.split("/", 1)[1] for i in ids if i.startswith("models/")}

    async def chat(self, messages, tools=None, on_token=None) -> Reply:
        body = {**self.params, "model": self.model, "messages": messages, "stream": True,
                "stream_options": {"include_usage": True}}
        if tools:
            body["tools"] = tools
        try:
            async with self._client.stream("POST", f"{self.base_url}/chat/completions",
                                           json=body, headers=self._headers) as resp:
                if resp.status_code != 200:
                    detail = (await resp.aread()).decode("utf-8", "replace")[:500]
                    raise _status_error(resp.status_code, detail)
                return await _read_stream(resp, on_token)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as e:
            raise Unavailable(f"{self.name}: {type(e).__name__}: {e}") from e


SPEED_PROMPT = "Write a Python function that returns the n-th Fibonacci number."


class OllamaAdmin:
    """Ollama's native API, for what the OpenAI-compatible endpoint lacks: model list,
    pull, and generation timings for the speed test."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434",
                 client: httpx.AsyncClient | None = None, timeout: float = 600):
        self.base_url = base_url.rstrip("/").removesuffix("/v1")
        self._client = client or httpx.AsyncClient(timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _post(self, path: str, body: dict) -> dict:
        try:
            resp = await self._client.post(self.base_url + path, json=body)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise Unavailable(f"ollama: {type(e).__name__}: {e}") from e
        if resp.status_code != 200:
            raise _status_error(resp.status_code, resp.text[:300])
        return resp.json()

    async def installed(self) -> set[str]:
        try:
            resp = await self._client.get(self.base_url + "/api/tags")
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise Unavailable(f"ollama: {type(e).__name__}: {e}") from e
        return {m["name"] for m in resp.json().get("models", [])}

    async def loaded(self) -> dict[str, int]:
        """Models Ollama currently holds in memory: name -> bytes (from /api/ps)."""
        try:
            resp = await self._client.get(self.base_url + "/api/ps")
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise Unavailable(f"ollama: {type(e).__name__}: {e}") from e
        return {m["name"]: int(m.get("size", 0)) for m in resp.json().get("models", [])}

    async def pull(self, name: str) -> None:
        """Download a model. Callers must get the user's confirmation first."""
        await self._post("/api/pull", {"model": name, "stream": False})

    async def tokens_per_second(self, name: str, num_predict: int = 64) -> float:
        """Generate a short reply and compute decode speed from Ollama's own timings."""
        data = await self._post("/api/generate", {
            "model": name, "prompt": SPEED_PROMPT, "stream": False,
            "options": {"num_predict": num_predict, "temperature": 0}})
        count, duration_ns = data.get("eval_count", 0), data.get("eval_duration", 0)
        if not count or not duration_ns:
            raise BadResponse(f"ollama returned no timings for {name}")
        return round(count / (duration_ns / 1e9), 1)


async def _read_stream(resp: httpx.Response, on_token) -> Reply:
    reply = Reply()
    calls: dict[int, dict] = {}
    async for line in resp.aiter_lines():
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError as e:
            raise BadResponse(f"bad stream chunk: {data[:200]}") from e
        if chunk.get("usage"):
            reply.usage = chunk["usage"]
        for choice in chunk.get("choices") or []:
            delta = choice.get("delta") or {}
            if delta.get("content"):
                reply.content += delta["content"]
                if on_token:
                    on_token(delta["content"])
            # Tool calls arrive as fragments keyed by index; concatenate name and arguments.
            for tc in delta.get("tool_calls") or []:
                slot = calls.setdefault(tc.get("index", len(calls)), {
                    "id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                slot["id"] = tc.get("id") or slot["id"]
                fn = tc.get("function") or {}
                slot["function"]["name"] += fn.get("name") or ""
                args = fn.get("arguments") or ""
                slot["function"]["arguments"] += args if isinstance(args, str) else json.dumps(args)
    reply.tool_calls = [calls[i] for i in sorted(calls)]
    return reply
