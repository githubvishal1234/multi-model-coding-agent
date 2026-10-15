"""Tool interface, shared context, argument validation and the default tool set."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ValidationError

from ferrule import safety
from ferrule.config import Settings
from ferrule.events import ApprovalRequest, Approver
from ferrule.safety import AuditLog, SafetyError


class ToolResult(BaseModel):
    ok: bool
    output: str = ""
    error: str | None = None


@dataclass
class ToolCall:
    name: str
    args: dict
    id: str = ""


class InvalidToolCall(Exception):
    """Unknown tool or arguments that fail validation. The message is sent back to the model."""


@dataclass
class ToolContext:
    settings: Settings
    approver: Approver
    audit: AuditLog
    # path -> content before the agent first touched it (None = the agent created it). Used by undo.
    originals: dict[str, str | None] = field(default_factory=dict)

    def resolve(self, path: str) -> Path:
        return safety.resolve(self.settings.workspace, path)

    async def approve(self, req: ApprovalRequest) -> bool:
        ok = await self.approver.approve(req)
        self.audit.write("approval", kind=req.kind, summary=req.summary, approved=ok)
        return ok

    def remember(self, path: Path) -> None:
        """Snapshot a file before its first change in this run."""
        key = str(path)
        if key not in self.originals:
            if path.exists():
                with open(path, encoding="utf-8", errors="replace", newline="") as f:
                    self.originals[key] = f.read()
            else:
                self.originals[key] = None


class Tool:
    name: ClassVar[str]
    description: ClassVar[str]
    Args: ClassVar[type[BaseModel]]
    read_only: ClassVar[bool] = False

    async def run(self, args, ctx: ToolContext) -> ToolResult:
        raise NotImplementedError

    def schema(self) -> dict:
        return {"type": "function", "function": {
            "name": self.name, "description": self.description,
            "parameters": self.Args.model_json_schema(),
        }}


def validate(tools: dict[str, Tool], call: ToolCall) -> tuple[Tool, BaseModel]:
    tool = tools.get(call.name)
    if tool is None:
        raise InvalidToolCall(f"unknown tool '{call.name}'. Available tools: {', '.join(tools)}")
    try:
        return tool, tool.Args.model_validate(call.args)
    except ValidationError as e:
        problems = "; ".join(
            f"{'.'.join(map(str, err['loc'])) or 'args'}: {err['msg']}" for err in e.errors()
        )
        raise InvalidToolCall(f"invalid arguments for {call.name}: {problems}. "
                              f"Usage: {tool.description}") from None


async def run_tool(tool: Tool, args: BaseModel, ctx: ToolContext) -> ToolResult:
    ctx.audit.write("tool_call", tool=tool.name, args=args.model_dump())
    try:
        result = await tool.run(args, ctx)
    except SafetyError as e:
        result = ToolResult(ok=False, error=f"refused: {e}")
    except OSError as e:
        result = ToolResult(ok=False, error=f"{type(e).__name__}: {e}")
    limit = ctx.settings.max_output_chars
    if len(result.output) > limit:
        cut = len(result.output) - limit
        result.output = result.output[:limit] + f"\n... [truncated {cut} chars]"
    ctx.audit.write("tool_result", tool=tool.name, ok=result.ok, error=result.error)
    return result


def default_tools() -> dict[str, Tool]:
    from ferrule.tools.commands import RunCommand, RunTests
    from ferrule.tools.files import EditFile, ReadFile, SearchRepo, WriteFile

    return {t.name: t for t in (ReadFile(), SearchRepo(), WriteFile(), EditFile(),
                                RunCommand(), RunTests())}
