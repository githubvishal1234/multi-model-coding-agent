import asyncio
import json

import httpx
import pytest

from ferrule.providers import BadResponse, OpenAICompatProvider, RateLimited, Unavailable


def sse(*chunks) -> bytes:
    return ("".join(f"data: {json.dumps(c)}\n\n" for c in chunks) + "data: [DONE]\n\n").encode()


def delta(**d):
    return {"choices": [{"index": 0, "delta": d}]}


def make(handler, **kw):
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return OpenAICompatProvider("http://test/v1", "m", client=client, **kw)


def chat(provider, **kw):
    return asyncio.run(provider.chat([{"role": "user", "content": "hi"}], **kw))


def test_streamed_content_is_reassembled():
    body = sse(delta(content="Hel"), delta(content="lo"),
               {"choices": [], "usage": {"prompt_tokens": 3, "completion_tokens": 2}})
    tokens = []
    reply = chat(make(lambda req: httpx.Response(200, content=body)), on_token=tokens.append)
    assert reply.content == "Hello" and tokens == ["Hel", "lo"]
    assert reply.usage == {"prompt_tokens": 3, "completion_tokens": 2}


def test_tool_call_fragments_are_reassembled():
    first = {"name": "read_file", "arguments": '{"pa'}
    body = sse(
        delta(tool_calls=[{"index": 0, "id": "c1", "function": first}]),
        delta(tool_calls=[{"index": 0, "function": {"arguments": 'th": "a.py"}'}}]),
    )
    reply = chat(make(lambda req: httpx.Response(200, content=body)))
    expected = {"name": "read_file", "arguments": '{"path": "a.py"}'}
    assert reply.tool_calls == [{"id": "c1", "type": "function", "function": expected}]


def test_request_body_and_auth_header():
    seen = {}

    def handler(req):
        seen["body"] = json.loads(req.content)
        seen["auth"] = req.headers.get("authorization")
        return httpx.Response(200, content=sse(delta(content="ok")))

    p = make(handler, api_key="secret-key-123", params={"temperature": 0, "seed": 7})
    chat(p, tools=[{"type": "function", "function": {"name": "x"}}])
    assert seen["body"]["model"] == "m" and seen["body"]["stream"] is True
    assert seen["body"]["temperature"] == 0 and seen["body"]["seed"] == 7
    assert seen["body"]["tools"][0]["function"]["name"] == "x"
    assert seen["auth"] == "Bearer secret-key-123"
    assert "secret-key-123" not in repr(p)


@pytest.mark.parametrize("status,error", [(429, RateLimited), (500, Unavailable),
                                          (503, Unavailable), (404, BadResponse)])
def test_http_errors_are_classified(status, error):
    with pytest.raises(error):
        chat(make(lambda req: httpx.Response(status, text="nope")))


def test_connection_refused_is_unavailable():
    def handler(req):
        raise httpx.ConnectError("refused")

    with pytest.raises(Unavailable):
        chat(make(handler))


def test_garbage_stream_is_bad_response():
    with pytest.raises(BadResponse):
        chat(make(lambda req: httpx.Response(200, content=b"data: {not json\n\n")))
