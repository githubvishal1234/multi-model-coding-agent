"""Command-line interface: ferrule run | plan | undo."""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from ferrule.agent import Agent
from ferrule.config import Settings
from ferrule.events import CliApprover, Event
from ferrule.providers import OpenAICompatProvider
from ferrule.undo import undo


def print_event(e: Event) -> None:
    d = e.data
    if e.kind == "token":
        print(d["text"], end="", flush=True)
    elif e.kind == "tool_call":
        print(f"\n-> {d['tool']} {json.dumps(d['args'])[:300]}")
    elif e.kind == "tool_result":
        print(f"<- {d['tool']}: " + ("ok" if d["ok"] else f"failed: {d['error']}"))
    elif e.kind in ("error", "stopped"):
        print(f"\n[{e.kind}] {d.get('message', '')}")


async def _run(settings: Settings, task: str, plan: bool):
    provider = OpenAICompatProvider(settings.base_url, settings.model,
                                    timeout=settings.model_timeout)
    try:
        return await Agent(provider, settings, CliApprover(), print_event).run(task, plan=plan)
    finally:
        await provider.aclose()


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(errors="replace")  # model output may not fit the console encoding
    parser = argparse.ArgumentParser(prog="ferrule",
                                     description="Local coding agent for free models.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("run", "run a task"),
                            ("plan", "propose a plan, then run it after approval")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("task")
        p.add_argument("--model", help="model name (default: FERRULE_MODEL or qwen2.5-coder:7b)")
        p.add_argument("--max-steps", type=int)
        p.add_argument("--workspace", type=Path, help="default: current directory")
        p.add_argument("--no-native-tools", action="store_true",
                       help="prompted JSON tool calls, for models without function calling")
    p = sub.add_parser("undo", help="restore files changed by the last run")
    p.add_argument("--workspace", type=Path)
    args = parser.parse_args(argv)

    settings = Settings.from_env(
        workspace=args.workspace,
        model=getattr(args, "model", None),
        max_steps=getattr(args, "max_steps", None),
        supports_tools=False if getattr(args, "no_native_tools", False) else None,
    )
    if not settings.workspace.is_dir():
        print(f"error: workspace folder does not exist: {settings.workspace}", file=sys.stderr)
        return 2
    if args.command == "undo":
        restored = undo(settings)
        print("\n".join(f"restored {f}" for f in restored) or "nothing to undo")
        return 0

    result = asyncio.run(_run(settings, args.task, plan=args.command == "plan"))
    print(f"\n[{result.status}] steps={result.steps} usage={result.usage}")
    return 0 if result.status == "done" else 1
