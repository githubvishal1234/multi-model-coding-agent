# Evaluation report (in progress)

Only numbers from runs that actually happened are listed here. Each one links to its result folder, which holds `results.csv`, `meta.json` (model digest, config hash, commit) and per-task transcripts. Phase 10 completes this report.

## Machine

From `ferrule doctor` on 2026-10-15: 23.8 GB RAM (11.7 GB free at the time), 4 CPU cores, NVIDIA GeForce GTX 1650 with 4.0 GB VRAM (3.8 GB free).

## Local model speed

| Model | Decode speed | How measured |
|---|---|---|
| qwen2.5-coder:7b | 7.7 tokens/s | `ferrule doctor`: one 64-token reply, from Ollama's own `eval_count / eval_duration` |

This is a single short measurement, so treat it as approximate. Other models haven't been measured yet. `qwen2.5-coder:14b` passes the memory estimate (about 9.9 GB against a 10.8 GB budget) but isn't installed, so it hasn't been tested.

## Task set results: qwen2.5-coder:7b, 20 tasks

All runs used `temperature: 0, seed: 42`, ran each task once, and auto-approved inside a temporary copy of the task repo.

| Run | Change being tested | Passed | Total time | Result folder |
|---|---|---|---|---|
| 1 | Baseline (prompted tool calls) | 5/20 | 32.8 min | `eval/results/20261015T105919Z_example` |
| 2 | + transcripts, "no changes" and "run the tests" nudges | 5/20 | 39.0 min | `eval/results/20261015T115807Z_example` |
| 3 | + `write_file`, clearer tool errors, `max_tokens` cap | 5/20 | 45.3 min | `eval/results/20261015T150021Z_example` |
| 4 | Same code as run 3, **native tool calls** | 6/20 | 25.5 min | `eval/results/20261015T152846Z_native` |

What these runs show:
- **Run-to-run variation is about ±2 tasks.** Across the four runs, 10 different tasks passed at least once, but never more than 6 in the same run. One run per configuration can't separate small effects from noise.
- **The loop changes fixed the specific failures they targeted**, as the transcripts show:
  - `fix_mutable_default` first passed once `write_file` existed.
  - The "run the tests" nudge caught the model inventing a passing test result.

  The total didn't move, because the remaining failures come from the model's reasoning: wrong edits, broken indentation, and misreading the task.
- **Native tool calls** gave the same or slightly better results in about 40% less time than prompted mode, because they avoid the model's JSON-escaping mistakes.

## Router with hosted fallback (2026-10-15)

Both runs used `eval/configs/router.yaml`: local `qwen2.5-coder:7b` first, escalating to `poolside/laguna-s-2.1:free` (OpenRouter), with Gemini as a fallback.

| Run | Passed | Total time | What happened | Result folder |
|---|---|---|---|---|
| R1 | 4/20 | not comparable | Router bugs: the local model was excluded once it was loaded (memory check); `gemini-2.5-flash` returned 404 to new users | `eval/results/20261015T163741Z_router` |
| R2 | 5/20 | 44.9 min | Bugs fixed. 16 of 20 tasks ended on the local model without escalating. The escalated ones hit `laguna-s-2.1:free` "temporarily rate-limited upstream", and Gemini rejected the `seed` field | `eval/results/20261015T173235Z_router` |

What R2 shows:
- **Free hosted capacity was the bottleneck, not the routing logic.** Every escalation landed on an overloaded free model, waited, and ran out of time.
- **Escalation triggers were too narrow.** Most tasks ended with a confident but wrong "done" on the local model. After R2 these were added:
  - a final answer right after a failing test run now escalates
  - Gemini no longer receives `seed`
  - waits are capped per model call

  These haven't been measured yet. When rechecked the same day, Gemini returned "503 high demand", so a rerun was postponed.

## Router on Groq `openai/gpt-oss-120b` (2026-11-26)

Same `eval/configs/router.yaml` (post-R2 fixes), with only `GROQ_API_KEY` set. Ollama wasn't running, so every model call went to Groq's free tier. `llama-3.3-70b-versatile` returned 404 `model_not_found` for this account and was removed from the registry.

| Run | Passed | Result folder |
|---|---|---|
| G0 (smoke, 3 tasks) | 3/3 (add_lines_flag, docstring_area, fix_median) | `eval/results/20261126T040920Z_router` |
| G1 (20 tasks) | 6/20 | `eval/results/20261126T043633Z_router` |

What G1 shows:
- **Only 12 of 20 tasks reached the model.** Groq returned 429 on tokens per minute 15 times and on **tokens per day** 8 times. After task 12 the daily cap was used up, so the last 8 tasks (all 3 `tests` tasks among them) failed with `provider_error` and 0 steps. That's a quota limit, not a model result.
- **On the 12 tasks that ran, 6 passed:** answer_db_config, docstring_area, fix_from_traceback, fix_median, fix_pagination, fix_restock_big_module. That compares with the local 7B model's best of 6/20, but the samples are different, so treat it as a rough signal.
- **Run-to-run variation still shows.** `add_lines_flag` passed in G0 and failed in G1.
- Failures on the tasks that ran: 3 wrong edits on boilerplate tasks, `explain_order_sync` never wrote ANSWER.json, `extract_tax_rate` hit max_steps, and `fix_mutable_default` was still wrong.

A full 20-task measurement on this free tier needs either two days (about 10 tasks per day's quota) or a run split with `--task`.

Fixes made after G1, from its transcripts:
- The task message now includes the workspace file list (up to 100 paths).
- There's a new read-only `list_files` tool.
- `search_repo` also matches file names.
- An empty reply (no text, no tool call) is retried instead of ending the run.

These haven't been measured yet. One rerun of `add_version_route` (`eval/results/20261126T050911Z_router`) shows the model calling `list_files` and reading `app.py` in its first two steps, where G1 spent its steps on refused `ls`/`git` commands. It then hit the daily token limit before finishing, so it doesn't count as a result. A second attempt at all 6 G1 failures (`eval/results/20261126T052633Z_router`) failed every task at step 0 on "tokens per day", even though `ferrule doctor`'s 5-token test request succeeded just before. Not a result either.

## Classifier

The rule-based task classifier (`ferrule/router.py`) agrees with the hand-written class labels on 16 of the 20 eval tasks. That's measured by `tests/test_router.py::test_eval_task_labels_vs_classifier`. The long-context tasks are recognised by repository size, not by their instructions.

## Not measured yet

- **Router with hosted fallback after the R2 fixes, on all 20 tasks.** Run G1 above covered 12 tasks before Groq's daily token cap.
- **Latency targets (N9).** To be set from these measurements once the hosted comparison exists.
- **Web lookup on vs off.** That's Phase 6.
