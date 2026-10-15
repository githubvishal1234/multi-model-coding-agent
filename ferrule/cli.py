"""Command-line interface: ferrule run | plan | doctor | undo."""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from ferrule.agent import Agent
from ferrule.config import Settings, load_dotenv
from ferrule.events import CliApprover, Event
from ferrule.hardware import detect, estimate_gb, load_speeds, save_speeds, select_local
from ferrule.providers import OllamaAdmin, OpenAICompatProvider, ProviderError
from ferrule.registry import load_registry
from ferrule.router import build_provider, installed_models, loaded_gb
from ferrule.undo import undo


def print_event(e: Event) -> None:
    d = e.data
    if e.kind == "token":
        print(d["text"], end="", flush=True)
    elif e.kind == "tool_call":
        print(f"\n-> {d['tool']} {json.dumps(d['args'])[:300]}")
    elif e.kind == "tool_result":
        print(f"<- {d['tool']}: " + ("ok" if d["ok"] else f"failed: {d['error']}"))
    elif e.kind == "routing":
        print(f"\n[routing] {d['task_class']} -> {d['chosen']} ({d['reason']})")
    elif e.kind in ("error", "stopped", "notice"):
        print(f"\n[{e.kind}] {d.get('message', '')}")


async def _run(settings: Settings, task: str, plan: bool):
    provider = await build_provider(settings, task)
    try:
        return await Agent(provider, settings, CliApprover(), print_event).run(task, plan=plan)
    finally:
        await provider.aclose()


async def _doctor(settings: Settings, speed_test: bool, offer_pull: bool) -> int:
    hw = detect(disk_path=settings.workspace)
    gpu = (f"{hw.gpu_name}, {hw.vram_free_gb}/{hw.vram_total_gb} GB VRAM free"
           if hw.gpu_name else "no NVIDIA GPU detected")
    print(f"RAM {hw.ram_free_gb}/{hw.ram_total_gb} GB free | {hw.cpu_cores} CPU cores | "
          f"{hw.disk_free_gb} GB disk free | {gpu}")

    registry = load_registry()
    local = [m for m in registry.models if registry.is_local(m)]
    installed = await installed_models(settings.base_url)
    if installed is None:
        print(f"Ollama is not reachable at {settings.base_url}; start it from the Ollama app.")
    else:
        print(f"Ollama models installed: {', '.join(sorted(installed)) or 'none'}")
    speeds = load_speeds(settings.home)
    too_slow = {m for m, tps in speeds.items() if tps < settings.min_tokens_per_sec}
    sel = select_local(local, hw, installed, override=settings.model, too_slow=too_slow,
                       loaded_gb=await loaded_gb(settings.base_url))
    print("\nLocal model selection (memory figures are estimates):")
    print("\n".join(sel.lines))

    admin = OllamaAdmin(settings.base_url)
    try:
        if sel.needs_pull and offer_pull:
            spec = next((m for m in local if m.name == sel.chosen), None)
            size = f" (~{estimate_gb(spec)} GB in memory)" if spec else ""
            answer = input(f"\n{sel.chosen} is not installed. Download it now{size}? [y/N] ")
            if answer.strip().lower() in ("y", "yes"):
                print(f"pulling {sel.chosen} ...")
                await admin.pull(sel.chosen)
                installed = (installed or set()) | {sel.chosen}
        if speed_test and installed:
            print(f"\nSpeed test (minimum {settings.min_tokens_per_sec} tokens/s):")
            order = [sel.chosen] if settings.model else sel.fitting
            for name in [n for n in order if n in installed]:
                try:
                    tps = await admin.tokens_per_second(name)
                except ProviderError as e:
                    print(f"  {name}: failed to run ({e}); stepping down")
                    continue
                save_speeds(settings.home, {name: tps})
                ok = tps >= settings.min_tokens_per_sec
                print(f"  {name}: {tps} tokens/s " + ("-> use this one" if ok else
                                                      "-> too slow, stepping down"))
                if ok:
                    break
    finally:
        await admin.aclose()
    usable = [n for n in sel.fitting if installed and n in installed
              and load_speeds(settings.home).get(n, 1e9) >= settings.min_tokens_per_sec]
    if settings.model:
        print(f"\nLocal model in use: {settings.model} (override)")
    elif usable:
        print(f"\nLocal model the router will use first: {usable[0]}")
        if sel.needs_pull:
            print(f"  ({sel.chosen} would fit but is not installed; run doctor again to "
                  f"download it, then it is speed-tested)")
    else:
        print("\nNo usable local model: install one with `ollama pull`, or set up a hosted key.")

    print("\nHosted providers:")
    for pname, p in registry.providers.items():
        if p.local:
            continue
        models = [m.name for m in registry.models if m.provider == pname]
        if not p.available(os.environ):
            print(f"  {pname}: off (set {p.api_key_env} to enable)")
            continue
        for m in models:
            # A listed model can still refuse requests (seen with Gemini), so send a tiny one.
            client = OpenAICompatProvider(p.base_url, m, api_key=p.api_key(os.environ),
                                          name=pname, is_local=False, timeout=60,
                                          params={"max_tokens": 5})
            try:
                await client.chat([{"role": "user", "content": "Reply with: ok"}])
                print(f"  {pname}: {m} works")
            except ProviderError as e:
                print(f"  {pname}: {m} FAILED: {' '.join(str(e).split())[:200]}")
            finally:
                await client.aclose()
    if settings.local_only:
        print("  local-only mode is on: hosted providers will not be used")
    return 0


def main(argv: list[str] | None = None) -> int:
    load_dotenv(Path.cwd() / ".env")  # API keys; real env vars win
    sys.stdout.reconfigure(errors="replace")  # model output may not fit the console encoding
    parser = argparse.ArgumentParser(prog="ferrule",
                                     description="Local coding agent for free models.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("run", "run a task"),
                            ("plan", "propose a plan, then run it after approval")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("task")
        p.add_argument("--model", help="use this Ollama model instead of the router")
        p.add_argument("--max-steps", type=int)
        p.add_argument("--workspace", type=Path, help="default: current directory")
        p.add_argument("--no-native-tools", action="store_true",
                       help="prompted JSON tool calls, for models without function calling")
        p.add_argument("--local-only", action="store_true",
                       help="never send code to hosted providers")
        p.add_argument("--profile", choices=["fast", "balanced", "quality"])
    p = sub.add_parser("doctor", help="show hardware, choose a local model, check providers")
    p.add_argument("--model", help="override the local model choice")
    p.add_argument("--no-speed-test", action="store_true")
    p.add_argument("--no-pull", action="store_true", help="never offer to download a model")
    p.add_argument("--workspace", type=Path)
    p = sub.add_parser("undo", help="restore files changed by the last run")
    p.add_argument("--workspace", type=Path)
    args = parser.parse_args(argv)

    settings = Settings.from_env(
        workspace=args.workspace,
        model=getattr(args, "model", None),
        max_steps=getattr(args, "max_steps", None),
        supports_tools=False if getattr(args, "no_native_tools", False) else None,
        local_only=True if getattr(args, "local_only", False) else None,
        profile=getattr(args, "profile", None),
    )
    if not settings.workspace.is_dir():
        print(f"error: workspace folder does not exist: {settings.workspace}", file=sys.stderr)
        return 2
    if args.command == "undo":
        restored = undo(settings)
        print("\n".join(f"restored {f}" for f in restored) or "nothing to undo")
        return 0
    if args.command == "doctor":
        return asyncio.run(_doctor(settings, not args.no_speed_test, not args.no_pull))

    result = asyncio.run(_run(settings, args.task, plan=args.command == "plan"))
    print(f"\n[{result.status}] steps={result.steps} usage={result.usage}")
    return 0 if result.status == "done" else 1
