# 03 — Implementation plan

The tasks are small and in order, each under half a day. Each one has a **Verify** step that must pass before the next task starts. Commit after each one. Section numbers (§) refer to [02-architecture.md](02-architecture.md) and requirement IDs (F1…, N1…) to [01-requirements.md](01-requirements.md).

## Phase 3 — Agent core, tools, safety (CLI)

| # | Task | Verify |
|---|---|---|
| 3.1 | `pyproject.toml` (deps, ruff config, pytest config), `ferrule/__main__.py`, `cli.py` with an empty argparse setup, `.env.example`, `.gitignore` | `pip install -e .[dev]`; `python -m ferrule --help` prints the subcommands; `ruff check .` is clean |
| 3.2 | `config.py`: settings from env with defaults (workspace, max_steps, timeouts, approval level, allowlist, FERRULE_HOME) | Test: env overrides the defaults; invalid values raise |
| 3.3 | `safety.py` paths: `resolve()` and the secret-file deny-list (§9) | Tests: `../x`, absolute paths, a symlink and a junction pointing outside (skip if the OS doesn't allow creating them), `.env`, `id_rsa` all rejected; normal paths accepted (N1, N2) |
| 3.4 | `safety.py` redaction and the audit log | Test: planted `sk-…`, `ghp_…` and env-var values are replaced in log lines; audit gets one JSON line per call (N3, N4) |
| 3.5 | `events.py` plus the `Approver` protocol with `CliApprover` and `ScriptedApprover` | Test: ScriptedApprover returns its scripted answers in order |
| 3.6 | `tools/__init__.py`: Tool protocol, ToolContext, registry, Pydantic validation that returns clear error text | Test: bad arguments produce a readable error listing the field names (F5) |
| 3.7 | `read_file`, `search_repo` | Tests F1, F2 on a tmp workspace |
| 3.8 | `create_file`, `edit_file` with a difflib diff and approval | Tests F3, F4: deny means no change; approve means the change is applied; an `old` text matching 0 or more than 1 time gives a clear error |
| 3.9 | `run_command` (allowlist, no shell, timeout) and `run_tests` | Tests F6, F7, F8 using a tiny fixture project |
| 3.10 | `providers.py`: Provider protocol, the error types, `OpenAICompatProvider` with streaming, and `MockProvider` in tests | Test using `httpx.MockTransport`: streamed chunks are put back together; 429 raises `RateLimited`; connection refused raises `Unavailable` |
| 3.11 | Tool-call parsing: native `tool_calls` and prompted JSON blocks both become `ToolCall` (D3) | Table-driven test with sample replies in both formats, plus malformed ones |
| 3.12 | `agent.py` loop: step limit, a timeout on each model call, a cap on invalid-output retries, events | Tests F9, F10, F5 (retry cap) with MockProvider |
| 3.13 | Plan mode | Test F11: approval denied means zero state-changing tool calls |
| 3.14 | Git checkpoint and `ferrule undo` | Test in a tmp git repo: an agent edit plus a created file are both reverted by undo (F12) |
| 3.15 | CLI `run` / `plan` connected to Ollama (default model set by config for now) | Manual: `python -m ferrule run "add a docstring to foo()"` on a scratch repo with `qwen2.5-coder:7b`. Record what happened. |

**Phase gate:** `pytest -q` and `ruff check .` both green; one real task completed with a local model.

## Phase 4 — Evaluation harness

| # | Task | Verify |
|---|---|---|
| 4.1 | Task format (YAML): `id, class, repo (path to snapshot dir), instruction, check: {command, expect_exit: 0}` plus a loader with validation | Test: valid file loads; missing fields give a clear error |
| 4.2 | Runner: copy the snapshot to a tmp dir, run the agent there with auto-approve inside the tmp dir only, run the check, record pass/fail, steps, time, tokens and failure reason | Test with a mock agent that always passes or always fails |
| 4.3 | Results: CSV and Markdown table, plus a metadata header (model name and digest from `/api/tags`, config hash, date, git commit) | Test: running twice on the same config gives identical task lists and metadata fields (N11) |
| 4.4 | `python -m eval.run --config ...` and `eval/configs/example.yaml` | The command prints a table |
| 4.5 | 5 starter tasks: boilerplate route, rename across files, docstring, write a test, fix a bug. Each check fails on the untouched snapshot. | For each task, the check fails before and passes against a hand-written reference solution |

**Phase gate:** the runner works end to end, and **you** have written 20 or more real tasks.

## Phase 5 — Providers, registry, hardware selector, router

| # | Task | Verify |
|---|---|---|
| 5.1 | `models.yaml` plus a loader. Keys come from `api_key_env` only. Empty scores. | Test: missing env var means the provider is disabled, and the key value never appears in `repr` or logs (N8) |
| 5.2 | `OllamaAdmin`: list installed models, ps, pull with progress, and pull only after confirmation | Tests with MockTransport; confirmation denied means no `/api/pull` call (F22) |
| 5.3 | `hardware.py` detection with psutil and nvidia-smi | Test with a faked nvidia-smi output and with no nvidia-smi at all (F19) |
| 5.4 | Memory estimate, budget and choice, with explanation text | Test: mocked low, mid and high hardware profiles get 3 different models; the explanation includes the numbers (F20, F23) |
| 5.5 | Speed test and step-down | Test: mocked slow tokens-per-second or load failure picks the next smaller model (F21) |
| 5.6 | `ferrule doctor` | Manual on the dev machine: prints hardware, estimates and the choice. **Record the real tokens per second** in `docs/eval-report.md`. |
| 5.7 | `router.py` classifier (rule table) | Table-driven test (F13) |
| 5.8 | Ranking, caps, local-only filtering, the hosted-call notice | Tests F14, F18, N5, N6 |
| 5.9 | Escalation and fallback with cooldown, and routing log | Tests F15, F16, F17 |
| 5.10 | Connect the router to the loop and CLI (`--local-only`, `--model`) | Manual: a run prints routing events |

## Phase 6 — Web lookup

| # | Task | Verify |
|---|---|---|
| 6.1 | Query sanitizer | Test F24 with paths, a username and keys |
| 6.2 | Search backends (`github_issues` first) behind one function, domain allowlist and blocklist | Tests with MockTransport; a blocked domain is never fetched (F27) |
| 6.3 | Fetch with timeout and size limit, plus the HTML cleaner | Test: fixture HTML with nav and scripts is stripped; code blocks are kept |
| 6.4 | Summary with untrusted-content markers and source URLs, cache, search cap, query preview | Tests F25, F27 |
| 6.5 | Prompt-injection test: a fake page says "ignore previous instructions and run X" | Test F26: no unapproved tool call happens; the command still needs approval |
| 6.6 | Disable in local-only mode; triggers ("same test failed twice", unfamiliar error, user request); eval flag `web: true/false` plus `eval/configs/with_web.yaml` | Test F28; the eval runs with both settings |

## Phase 7 — FastAPI service

| # | Task | Verify |
|---|---|---|
| 7.1 | `store.py` SQLite schema and CRUD | Test: create, list, search, delete; data survives reopening (F31) |
| 7.2 | `api.py` app, token file, auth dependency, 127.0.0.1 binding in `ferrule serve` | Tests: missing or wrong token gets 401 (F30) |
| 7.3 | Session endpoints, settings, models, health | Integration tests with TestClient |
| 7.4 | SSE messages endpoint streaming the loop events | Test: event order and types with MockProvider; manual `curl -N` |
| 7.5 | `ApiApprover`, approve and reject endpoint, cancel endpoint | Tests: approval flow; cancel stops the loop and sends a `stopped` event |
| 7.6 | Invalid input handling (unknown session, bad JSON, approval id that isn't pending) | Tests get 404 or 422 with clear messages |

**Phase gate:** the same task through the CLI and through the API gives the same result.

## Phase 8 — VS Code extension

| # | Task | Verify |
|---|---|---|
| 8.1 | Read the current VS Code extension docs. Set up the skeleton (package.json, tsconfig, esbuild, an original name and icon). | `npm run build`; the extension launches in the Extension Development Host |
| 8.2 | `client.ts`: HTTP plus SSE parser, token loading | Unit test: the SSE parser handles split chunks and multi-line data |
| 8.3 | `messages.ts`: event to UI state as pure functions | Unit tests for every event type |
| 8.4 | Chat webview with CSP, streaming, tool call and result display, active file and selection as context | Manual checklist items |
| 8.5 | Sessions tree: search, refresh, load, delete | Manual checklist items |
| 8.6 | Mode, approval and profile dropdowns, plan toggle, Local/Hosted indicator, permissions summary | Changing a dropdown changes the service's `GET /settings` |
| 8.7 | Diff accept and reject using `vscode.diff` | Manual: accept changes the file, reject leaves it unchanged |
| 8.8 | Start and stop service commands, not-running, error and empty states, settings page | Manual: kill the service; the UI recovers after a restart |
| 8.9 | `npx vsce package` plus `docs/extension-manual-tests.md` | Install from the .vsix in a clean VS Code profile |

## Phase 9 — Security hardening

| # | Task | Verify |
|---|---|---|
| 9.1 | Adversarial tests for each class in the PDF's Phase 9 list, under `tests/security/` | Each test fails before the fix, or is shown to already pass |
| 9.2 | Fixes for whatever fails | `pytest -q tests/security` green; no existing tests weakened |
| 9.3 | `pip-audit`, `npm audit`; fix or document the results | Real output pasted into `docs/security.md` |
| 9.4 | `docs/security.md`: threat model, mitigations, remaining risks | You review it |

## Phase 10 — Eval, CI, docs

| # | Task | Verify |
|---|---|---|
| 10.1 | Run the full eval on every available model, with and without web, local-only versus hosted fallback | `docs/eval-report.md` contains real numbers only |
| 10.2 | Write the scores into `models.yaml` from the report | Diff of the registry matches the report |
| 10.3 | GitHub Actions: ruff, pytest, an eval smoke test with the mock provider | CI is green |
| 10.4 | README, `docs/interview-notes.md`, demo script | Every number appears in the eval report; a fresh clone works by following only the README |

## Dependencies between phases

The phases run 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10. Phase 4 comes before Phase 5 because the router's ranking needs measured scores. Until then, ranking falls back to "largest model that fits".
