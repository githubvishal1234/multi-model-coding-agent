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

## Classifier

The rule-based task classifier (`ferrule/router.py`) agrees with the hand-written class labels on 16 of the 20 eval tasks. That's measured by `tests/test_router.py::test_eval_task_labels_vs_classifier`. The long-context tasks are recognised by repository size, not by their instructions.

## Not measured yet

- **Router with hosted fallback after the R2 fixes.** Waiting for free hosted capacity (see above).
- **Latency targets (N9).** To be set from these measurements once the hosted comparison exists.
- **Web lookup on vs off.** That's Phase 6.
