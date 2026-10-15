# Ferrule

> **Work in progress.** "Ferrule" is a working name. This README is a placeholder; the full version (architecture diagram, evaluation results, demo) comes when the project is finished.

Ferrule is a local coding agent that runs on **free models**, either local through [Ollama](https://ollama.com) or free hosted tiers, and aims to pick the best available model for each task. It reads and searches a repository, proposes edits as diffs, and runs commands and tests. Every change needs your approval.

## Status

| Phase | Area | State |
|---|---|---|
| 1–2 | Requirements, architecture, plan ([docs/](docs/)) | done |
| 3 | Agent core, tools, safety layer, CLI | done |
| 4 | Evaluation harness ([eval/](eval/)) | done; task set being written |
| 5 | Model router, hardware-aware model selection, hosted providers | next |
| 6 | Web lookup tool | planned |
| 7 | Local FastAPI service with streaming | planned |
| 8 | VS Code extension | planned |
| 9 | Security review and hardening | planned |
| 10 | Full evaluation, CI, documentation | planned |

## Quick start

Requires Python 3.12+ and Ollama with a coding model pulled (e.g. `ollama pull qwen2.5-coder:7b`).

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"     # on macOS/Linux: .venv/bin/python
.venv/Scripts/python -m ferrule run "Add a docstring to foo() in calc.py" --workspace path/to/project
```

- `ferrule plan "..."` proposes numbered steps and runs nothing until you approve them.
- `ferrule undo` restores the files changed by the last run.
- Add `--no-native-tools` for models without function calling.
- Settings are `FERRULE_*` environment variables; see [.env.example](.env.example).

## Safety model

- File access is confined to the workspace. `..`, absolute paths, symlinks and junctions that point outside are rejected, and so are secret files (`.env`, keys) and `.git`.
- Edits, new files, commands and test runs need approval. Edits are shown as a diff first.
- Commands are limited to an allowlist, run without a shell, and have a timeout.
- Secrets are redacted from the audit log (`~/.ferrule/audit.log`).
- Model output, file contents and tool output are treated as data, never as instructions.

## Development

```bash
.venv/Scripts/python -m pytest -q      # unit tests; no model or network needed
.venv/Scripts/ruff check .
.venv/Scripts/python -m eval.run --config eval/configs/example.yaml   # evaluation (needs Ollama)
```

## Limitations

Free and local models are much weaker than top hosted models. They do best on small, well-defined tasks (boilerplate, docstrings, small fixes) and often fail on larger ones. No benchmark numbers are published yet; they will come from the evaluation harness, not from estimates.
