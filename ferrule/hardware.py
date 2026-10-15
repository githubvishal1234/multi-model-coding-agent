"""Hardware detection and local model selection.

Memory needs are ESTIMATES from a rule of thumb, not measurements: a 4-bit model needs about
0.6 GB per billion parameters, plus memory for the context (KV cache and runtime buffers).
The speed test then measures what the estimate cannot.
"""

import json
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import psutil

from ferrule.registry import ModelSpec

GB_PER_B_PARAMS = 0.6  # 4-bit weights, rule of thumb (estimate)
GB_PER_4K_CONTEXT = 0.5  # KV cache + buffers per 4k tokens of context (estimate)
SELECT_CONTEXT = 8192  # context size the estimate assumes
BUDGET_FRACTION = 0.7  # use at most 70% of currently free memory


@dataclass
class Hardware:
    ram_total_gb: float
    ram_free_gb: float
    cpu_cores: int
    disk_free_gb: float
    gpu_name: str | None = None
    vram_total_gb: float = 0.0
    vram_free_gb: float = 0.0

    def budget_gb(self) -> float:
        # Ollama splits layers between GPU and CPU, so free RAM and free VRAM both count.
        return round(BUDGET_FRACTION * (self.ram_free_gb + self.vram_free_gb), 1)


def _gb(n_bytes: float) -> float:
    return round(n_bytes / 1024**3, 1)


def _nvidia(run: Callable) -> tuple[str, float, float] | None:
    try:
        out = run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free",
                   "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):  # not installed, or the driver hung
        return None
    lines = out.stdout.strip().splitlines() if out.returncode == 0 else []
    try:
        # ponytail: first GPU only; multi-GPU machines would need per-device budgets.
        name, total, free = (part.strip() for part in lines[0].split(","))
        return name, round(float(total) / 1024, 1), round(float(free) / 1024, 1)
    except (IndexError, ValueError):
        return None


def detect(run: Callable = subprocess.run, disk_path: str | Path = ".") -> Hardware:
    vm = psutil.virtual_memory()
    gpu = _nvidia(run)
    return Hardware(
        ram_total_gb=_gb(vm.total), ram_free_gb=_gb(vm.available),
        cpu_cores=psutil.cpu_count(logical=False) or psutil.cpu_count() or 1,
        disk_free_gb=_gb(shutil.disk_usage(disk_path).free),
        gpu_name=gpu[0] if gpu else None,
        vram_total_gb=gpu[1] if gpu else 0.0, vram_free_gb=gpu[2] if gpu else 0.0,
    )


def estimate_gb(model: ModelSpec, context: int = SELECT_CONTEXT) -> float | None:
    if model.params_b is None:
        return None
    return round(model.params_b * GB_PER_B_PARAMS + GB_PER_4K_CONTEXT * context / 4096, 1)


@dataclass
class Selection:
    fitting: list[str]  # local models that fit and are not known to be too slow, largest first
    chosen: str | None
    needs_pull: bool
    lines: list[str] = field(default_factory=list)  # human-readable explanation of every choice


def select_local(models: list[ModelSpec], hw: Hardware, installed: set[str] | None = None,
                 override: str | None = None, too_slow: set[str] = frozenset()) -> Selection:
    """Pick the largest local model whose estimated memory fits the budget."""
    budget = hw.budget_gb()
    lines = [f"budget: {BUDGET_FRACTION:.0%} of (free RAM {hw.ram_free_gb} GB + free VRAM "
             f"{hw.vram_free_gb} GB) = {budget} GB"]
    fitting = []
    for m in sorted(models, key=lambda m: m.params_b or 0, reverse=True):
        est = estimate_gb(m)
        if est is None:
            lines.append(f"  {m.name}: size unknown, skipped")
        elif est > budget:
            lines.append(f"  {m.name}: needs ~{est} GB (estimate) > {budget} GB, skipped")
        elif m.name in too_slow:
            lines.append(f"  {m.name}: fits (~{est} GB) but measured too slow, skipped")
        else:
            state = "" if installed is None else (
                ", installed" if m.name in installed else ", not installed")
            lines.append(f"  {m.name}: fits (~{est} GB estimate{state})")
            fitting.append(m.name)
    if override:
        chosen = override
        lines.append(f"chosen: {override} (user override; fit checks not applied)")
    elif fitting:
        chosen = fitting[0]
        lines.append(f"chosen: {chosen} (largest model that fits)")
    else:
        chosen = None
        lines.append("chosen: none; no local model fits the memory budget")
    needs_pull = bool(chosen and installed is not None and chosen not in installed)
    return Selection(fitting, chosen, needs_pull, lines)


# Measured speeds are kept between runs: `ferrule doctor` writes them, the router reads them.
def load_speeds(home: Path) -> dict[str, float]:
    path = Path(home) / "speeds.json"
    try:
        return {k: float(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}
    except (OSError, ValueError, AttributeError):
        return {}


def save_speeds(home: Path, speeds: dict[str, float]) -> None:
    path = Path(home) / "speeds.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({**load_speeds(home), **speeds}, indent=2), encoding="utf-8")
