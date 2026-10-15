"""Shared test doubles. Tests need no model and no network."""

import asyncio

from ferrule.events import ScriptedApprover
from ferrule.providers import Reply
from ferrule.safety import AuditLog, Redactor
from ferrule.tools import ToolCall, ToolContext, default_tools, run_tool, validate


class MockProvider:
    """Returns scripted replies in order; the last one repeats. Records every request."""

    name = "mock"
    model = "mock-model"
    is_local = True

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls: list[dict] = []

    async def chat(self, messages, tools=None, on_token=None):
        self.calls.append({"messages": [dict(m) for m in messages], "tools": tools})
        r = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        if isinstance(r, Exception):
            raise r
        if on_token and r.content:
            on_token(r.content)
        return r


def tool_reply(name: str, **args) -> Reply:
    """A prompted-mode reply containing one fenced tool call."""
    import json
    return Reply(content=f'```tool\n{json.dumps({"tool": name, "args": args})}\n```')


def make_ctx(settings, answers=(), default=False):
    approver = ScriptedApprover(answers, default)
    ctx = ToolContext(settings, approver, AuditLog(settings.home / "audit.log", Redactor({})))
    return ctx, approver


def call(ctx, name, **args):
    tool, parsed = validate(default_tools(), ToolCall(name, args))
    return asyncio.run(run_tool(tool, parsed, ctx))
