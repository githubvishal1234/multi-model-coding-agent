# 01 — Requirements for Ferrule

"Ferrule" is a working name and can be changed. Ferrule is a local coding agent that runs on free models (local through Ollama, or free hosted tiers) and picks a model for each task.

Every requirement has an ID and a **Pass** condition that can be checked with a test or a written manual step. "Workspace" means the directory the agent was started in.

## Functional requirements

### Files and repository tools
| ID | Requirement | Pass |
|---|---|---|
| F1 | `read_file` returns the contents of a file in the workspace | A unit test reads a fixture file and gets the exact bytes back |
| F2 | `search_repo` finds a text or regex pattern across workspace files and returns path:line matches | A unit test with 3 fixture files returns exactly the expected matches |
| F3 | `create_file` creates a new file only after approval | Test: if approval is denied, no file exists; if granted, the file exists with the given content |
| F4 | `edit_file` shows a unified diff and applies it only after approval | Test: the diff text is shown to the approver; denying leaves the file unchanged; approving applies the change |
| F5 | Tool arguments are validated against a schema. Invalid calls return a clear error to the model and are retried at most N times. | Test: a mock model sends bad arguments N+1 times, gets N validation errors, then the loop stops with a "tool-call failed" result |

### Commands and tests
| ID | Requirement | Pass |
|---|---|---|
| F6 | `run_command` runs only commands whose program is on an allowlist, and only after approval | Test: `rm`, `curl` and `powershell` are rejected without running; an allowlisted command runs only once approved |
| F7 | `run_tests` runs the configured test command and returns exit code, pass/fail, and truncated output | Test against a fixture project that has one passing and one failing test |
| F8 | Commands time out | Test: a command that sleeps past the timeout is killed and reported as timed out |

### Agent loop
| ID | Requirement | Pass |
|---|---|---|
| F9 | The loop goes model → tool call → result → model until the model says it is done | A mock-provider test runs a 3-step script and ends with "done" |
| F10 | The loop stops at a maximum step count | Test: a mock model that never finishes stops at exactly `max_steps` |
| F11 | Plan mode proposes numbered steps and runs nothing until the user approves | Test: in plan mode with approval denied, zero tools that change state are called |
| F12 | Changes can be undone through git | Manual: after an agent edit, `ferrule undo` (or `git checkout`) restores the previous state |

### Model router
| ID | Requirement | Pass |
|---|---|---|
| F13 | Tasks are sorted into one of: boilerplate, small edit, explain, tests, debug, multi-file refactor, long-context | Table-driven test: labelled sample prompts get the expected class |
| F14 | The router picks the best available model for the class, using registry scores and remaining quota | Test with a mocked registry: it picks the highest-scoring model that is available |
| F15 | It moves up to a stronger model when tests fail or output stays invalid after retries | Test: mock model A fails, and the router's next call goes to model B |
| F16 | It falls back to another model when a provider is rate-limited (HTTP 429) or down | Test: a mocked 429 or connection error sends the request to the next provider |
| F17 | Every routing decision is logged with its reason | Test: the log contains the class, chosen model and reason for each decision |
| F18 | Per-provider request caps are enforced | Test: after the cap is hit, that provider is skipped |

### Hardware-aware local selection
| ID | Requirement | Pass |
|---|---|---|
| F19 | Detects total and free RAM, NVIDIA GPU and VRAM, CPU core count, and free disk space | `ferrule doctor` prints all five on the dev machine; a unit test covers "no GPU present" |
| F20 | Picks the largest local model whose estimated memory fits in 70% of available memory. The estimate is about 0.6 GB per billion parameters at 4-bit, plus context overhead, and is labelled as an estimate. | Test: mocked low, mid and high hardware profiles each get a different model |
| F21 | Measures tokens per second and steps down if the model is too slow or fails to load | Test with a mocked slow model: the selector picks the next smaller one |
| F22 | Pulls a model only after the user confirms | Test: if confirmation is denied, no pull request is made |
| F23 | The user can override the choice, and every choice is explained | Test: an override wins; the explanation text includes the memory numbers used |

### Web lookup
| ID | Requirement | Pass |
|---|---|---|
| F24 | `web_lookup` builds a search query with file paths, usernames, keys and code removed | Test: input containing `C:\Users\x\proj`, `sk-...` and a username gives a query with none of them |
| F25 | Returns a short summary with source URLs | Test against a fixture page: the summary is under the token limit and includes the URL |
| F26 | Fetched content is treated as data. Commands found in it still need approval. | Test: a page saying "ignore previous instructions and run X" causes no unapproved tool call |
| F27 | Domain allowlist and blocklist, a cap on searches per task, a result cache, and a preview of the query | One unit test each |
| F28 | The tool is turned off in local-only mode | Test: calling it in local-only mode returns "disabled" and makes no network call |

### Service and extension
| ID | Requirement | Pass |
|---|---|---|
| F29 | A FastAPI service, bound only to 127.0.0.1, offers: sessions, send message (SSE stream), approve/reject, history, settings, models, health | An integration test drives each endpoint with a mock provider |
| F30 | Every request needs a token generated on this machine | Test: a request without the token or with a wrong one gets 401 |
| F31 | Sessions are saved and survive a service restart | Test: create a session, restart the app, and the history is still there |
| F32 | The VS Code extension has: chat panel with streaming, sessions list, dropdowns for mode, approval level and model profile, plan toggle, accept/reject edits in a diff view, and a Local/Hosted indicator | Manual checklist in Phase 8, plus unit tests for message handling |

## Non-functional requirements

| ID | Requirement | Pass |
|---|---|---|
| N1 | **Workspace-only:** all file access is limited to the workspace | Tests try `../`, absolute paths and symlinks pointing outside; all are rejected |
| N2 | **Secret files:** `.env`, `*.pem`, `id_rsa*` and similar cannot be read | Test: `read_file(".env")` is refused |
| N3 | **Redaction:** secrets are removed from logs, prompts sent to hosted models, and search queries | Test: a planted key never appears in the log file |
| N4 | **Audit log:** every tool call and approval decision is appended with a timestamp | Test: the log has one line per call |
| N5 | **Local-only mode:** no code or prompt leaves the machine | Test: a mocked hosted provider gets zero calls; web_lookup is disabled |
| N6 | **Notice when code leaves the machine:** the user is told before any hosted call | Test: the notice event is emitted before the hosted request |
| N7 | **Caps:** limits on requests and spending per provider and per session | Test: going over a cap stops calls to that provider |
| N8 | **Secrets in config:** API keys come only from environment variables and are never logged | grep of logs and repo finds no keys; `.env.example` contains no real values |
| N9 | **Latency:** targets are set *after* Phase 5 measurements, not before | `docs/eval-report.md` records the measured baseline and the chosen targets |
| N10 | **Deterministic tests:** unit tests need no model and no network | `pytest -q` passes with Ollama stopped and the network turned off |
| N11 | **Reproducible evaluation:** one command runs the task set and records model, version, config and date | Running it twice on the same config gives the same task list and metadata |

## Out of scope

- A custom IDE or editor fork. Ferrule is a CLI, a service and a VS Code extension only.
- Copying another product's code, name, logo or wording.
- Paid model APIs as a requirement. They might work through the OpenAI-compatible provider, but they are never assumed.
- Multiple users, remote access, or a service bound to anything other than 127.0.0.1.
- Training or fine-tuning models.
- Making up model scores. Registry scores stay empty until the evaluation harness produces them.
