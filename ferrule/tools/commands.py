"""run_command (allowlist + approval) and run_tests (configured command)."""

import asyncio
import shutil
import subprocess

from pydantic import BaseModel, Field

from ferrule.events import ApprovalRequest
from ferrule.safety import check_command
from ferrule.tools import Tool, ToolContext, ToolResult

# Auto-approved in approval="auto_safe" mode. Fixed here, not configurable, on purpose.
SAFE_COMMANDS = {("git", "status"), ("git", "diff"), ("git", "log"), ("git", "show")}


def _run(argv: list[str], cwd, timeout: float) -> ToolResult:
    # ponytail: on timeout subprocess.run kills the child only; grandchildren holding the pipes
    # can still delay return on Windows. Use a job object / process group if that bites.
    try:
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return ToolResult(ok=False, error=f"timed out after {timeout:g}s")
    ok = proc.returncode == 0
    return ToolResult(ok=ok, output=f"exit code: {proc.returncode}\n{proc.stdout}{proc.stderr}",
                      error=None if ok else f"exit code {proc.returncode}")


class RunCommand(Tool):
    name = "run_command"
    description = ("Run an allowlisted program in the workspace, given as an argv list, e.g. "
                   '["git", "diff"]. No shell. Needs user approval.')

    class Args(BaseModel):
        argv: list[str] = Field(min_length=1)

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        s = ctx.settings
        prog = check_command(a.argv, s.allowlist)
        exe = shutil.which(prog)
        if exe is None:
            return ToolResult(ok=False, error=f"'{prog}' was not found on PATH")
        auto = s.approval == "auto_safe" and (prog, *a.argv[1:2]) in SAFE_COMMANDS
        cmd = " ".join(a.argv)
        if not auto and not await ctx.approve(ApprovalRequest("run_command", f"run: {cmd}")):
            return ToolResult(ok=False, error="the user rejected this command")
        return await asyncio.to_thread(_run, [exe, *a.argv[1:]], s.workspace, s.command_timeout)


class RunTests(Tool):
    name = "run_tests"
    description = "Run the project's configured test command and return the result."

    class Args(BaseModel):
        pass

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        s = ctx.settings
        cmd = " ".join(s.test_command)
        if s.approval != "auto_safe" and not await ctx.approve(
                ApprovalRequest("run_tests", f"run tests: {cmd}")):
            return ToolResult(ok=False, error="the user rejected running the tests")
        return await asyncio.to_thread(_run, s.test_command, s.workspace, s.command_timeout)
