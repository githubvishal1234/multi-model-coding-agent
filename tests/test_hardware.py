import asyncio
import subprocess
from types import SimpleNamespace

import httpx
import pytest

from ferrule.hardware import (
    Hardware,
    detect,
    estimate_gb,
    load_speeds,
    save_speeds,
    select_local,
)
from ferrule.providers import BadResponse, OllamaAdmin, Unavailable
from ferrule.registry import load_registry

LOCAL = [m for m in load_registry(env={}).models if m.provider == "ollama"]

LOW = Hardware(ram_total_gb=8, ram_free_gb=3, cpu_cores=2, disk_free_gb=50)
MID = Hardware(ram_total_gb=16, ram_free_gb=6, cpu_cores=4, disk_free_gb=100,
               gpu_name="GTX 1650", vram_total_gb=4, vram_free_gb=3)
HIGH = Hardware(ram_total_gb=64, ram_free_gb=12, cpu_cores=16, disk_free_gb=500,
                gpu_name="RTX 4070", vram_total_gb=12, vram_free_gb=8)


def fake_run(stdout="", returncode=0, exc=None):
    def run(*args, **kwargs):
        if exc:
            raise exc
        return SimpleNamespace(stdout=stdout, returncode=returncode)
    return run


# --- detection (F19) ---

def test_detect_with_nvidia_gpu():
    hw = detect(run=fake_run("NVIDIA GeForce GTX 1650, 4096, 3935\n"))
    assert hw.gpu_name == "NVIDIA GeForce GTX 1650"
    assert (hw.vram_total_gb, hw.vram_free_gb) == (4.0, 3.8)
    assert hw.ram_total_gb > 0 and hw.cpu_cores >= 1 and hw.disk_free_gb > 0


@pytest.mark.parametrize("run", [
    fake_run(exc=FileNotFoundError("nvidia-smi")),
    fake_run(exc=subprocess.TimeoutExpired("nvidia-smi", 10)),
    fake_run(stdout="", returncode=9),
    fake_run(stdout="garbage"),
])
def test_detect_without_usable_gpu(run):
    hw = detect(run=run)
    assert hw.gpu_name is None and hw.vram_free_gb == 0.0


# --- estimate and selection (F20, F23) ---

def test_estimate_follows_documented_rule():
    m7 = next(m for m in LOCAL if m.name == "qwen2.5-coder:7b")
    assert estimate_gb(m7) == round(7.6 * 0.6 + 1.0, 1)  # 0.6 GB/B params + 0.5 GB per 4k ctx


def test_low_mid_high_hardware_pick_different_models():
    picks = [select_local(LOCAL, hw).chosen for hw in (LOW, MID, HIGH)]
    assert picks == ["qwen2.5-coder:1.5b", "qwen2.5-coder:7b", "qwen2.5-coder:14b"]


def test_explanation_includes_numbers():
    sel = select_local(LOCAL, MID)
    text = "\n".join(sel.lines)
    assert "6.3 GB" in text  # 0.7 * (6 + 3)
    assert "qwen2.5-coder:14b: needs ~9.9 GB (estimate) > 6.3 GB, skipped" in text
    assert "chosen: qwen2.5-coder:7b" in text


def test_nothing_fits():
    tiny = Hardware(ram_total_gb=2, ram_free_gb=0.5, cpu_cores=1, disk_free_gb=5)
    sel = select_local(LOCAL, tiny)
    assert sel.chosen is None and sel.fitting == []


def test_override_wins_and_is_explained():
    sel = select_local(LOCAL, LOW, override="qwen2.5-coder:14b")
    assert sel.chosen == "qwen2.5-coder:14b" and "user override" in sel.lines[-1]


def test_not_installed_choice_needs_pull():
    sel = select_local(LOCAL, HIGH, installed={"qwen2.5-coder:7b"})
    assert sel.chosen == "qwen2.5-coder:14b" and sel.needs_pull
    assert not select_local(LOCAL, MID, installed={"qwen2.5-coder:7b"}).needs_pull


def test_too_slow_models_step_down():  # F21
    sel = select_local(LOCAL, HIGH, too_slow={"qwen2.5-coder:14b"})
    assert sel.chosen == "qwen2.5-coder:7b"


def test_speeds_round_trip(tmp_path):
    assert load_speeds(tmp_path) == {}
    save_speeds(tmp_path, {"a": 12.5})
    save_speeds(tmp_path, {"b": 3.0})
    assert load_speeds(tmp_path) == {"a": 12.5, "b": 3.0}
    (tmp_path / "speeds.json").write_text("not json")
    assert load_speeds(tmp_path) == {}


# --- Ollama admin (F22) ---

def admin(handler):
    return OllamaAdmin("http://test:11434/v1",
                       client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


def test_installed_models():
    a = admin(lambda req: httpx.Response(200, json={"models": [{"name": "x:1"}, {"name": "y"}]}))
    assert asyncio.run(a.installed()) == {"x:1", "y"}


def test_speed_from_ollama_timings():
    seen = {}

    def handler(req):
        seen["path"] = req.url.path
        return httpx.Response(200, json={"eval_count": 64, "eval_duration": 8_000_000_000})

    assert asyncio.run(admin(handler).tokens_per_second("m")) == 8.0
    assert seen["path"] == "/api/generate"


def test_speed_without_timings_is_an_error():
    with pytest.raises(BadResponse):
        asyncio.run(admin(lambda req: httpx.Response(200, json={})).tokens_per_second("m"))


def test_pull_and_errors():
    calls = []

    def handler(req):
        calls.append(req.url.path)
        return httpx.Response(200, json={"status": "success"})

    asyncio.run(admin(handler).pull("m"))
    assert calls == ["/api/pull"]

    def down(req):
        raise httpx.ConnectError("refused")

    with pytest.raises(Unavailable):
        asyncio.run(admin(down).installed())
