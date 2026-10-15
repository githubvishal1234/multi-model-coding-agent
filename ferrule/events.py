"""Events the agent emits, and the approval interface."""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Event:
    kind: str  # token | plan | tool_call | tool_result | error | stopped | done
    data: dict = field(default_factory=dict)


Emit = Callable[[Event], None]


@dataclass
class ApprovalRequest:
    kind: str  # plan | write_file | edit_file | run_command | run_tests
    summary: str
    detail: str = ""


class Approver(Protocol):
    async def approve(self, req: ApprovalRequest) -> bool: ...


class CliApprover:
    async def approve(self, req: ApprovalRequest) -> bool:
        print(f"\n--- approval needed: {req.summary} ---")
        if req.detail:
            print(req.detail)
        try:
            answer = await asyncio.to_thread(input, "Approve? [y/N] ")
        except EOFError:
            return False
        return answer.strip().lower() in ("y", "yes")


class ScriptedApprover:
    """Answers from a fixed list, then `default`. Records every request (tests, eval)."""

    def __init__(self, answers=(), default: bool = False):
        self.answers = list(answers)
        self.default = default
        self.requests: list[ApprovalRequest] = []

    async def approve(self, req: ApprovalRequest) -> bool:
        self.requests.append(req)
        return self.answers.pop(0) if self.answers else self.default
