# 00 — Current state

Recorded 2026-10-15. Each line cites the command it came from.

## Repository

| Fact | Source |
|---|---|
| The directory was empty before this phase (no files, no README, no config, no dependencies) | `ls -la` showed only `.` and `..` |
| A git repository was created in this phase with no commits yet | `git init` → `git status`: "No commits yet, nothing to commit" |
| There is no application code and no tests, so nothing runs and no test results exist | follows from the empty listing |

Files added in this phase: `CLAUDE.md`, `docs/00-current-state.md`, `docs/01-requirements.md`.

## Development machine

| Fact | Source |
|---|---|
| Windows 11 Home 10.0.26300 | session environment |
| Python 3.14.4 | `python --version` |
| psutil is already installed and reports 23.75 GiB total RAM | `python -c "import psutil; ..."` |
| Node.js v24.15.0, needed for the Phase 8 extension | `node --version` |
| NVIDIA GeForce GTX 1650 with 4096 MiB VRAM | `nvidia-smi --query-gpu=name,memory.total` |
| Ollama client 0.33.2 is installed but was not running at first. `ollama list` started the server. | `ollama --version`, `ollama list` |
| Local models already pulled: `deepseek-coder:6.7b` (3.8 GB), `qwen2.5-coder:7b` (4.7 GB), `llama3.2:latest` (2.0 GB) | `ollama list` |

**Correction (Phase 3):** a plain `ollama serve` from a shell uses `~/.ollama` and sees only `llama3`, `llama3.1` and `nomic-embed-text`. The coder models above are only visible when the Ollama desktop app starts the server. Start Ollama from the app, or check `curl http://127.0.0.1:11434/api/tags`, before running Ferrule.

## Not yet measured

- Speed of any model on this machine, in tokens per second. This gets measured in Phase 5.
- Whether the 7B models fit fully in 4 GB of VRAM or spill to the CPU. Their file sizes (3.8 to 4.7 GB) suggest at least partial offload, but nothing has been tested yet.
- CPU model and free disk space. These were not captured in this phase.
