# Evaluation harness

```bash
python -m eval.run --config eval/configs/example.yaml                  # run the agent
python -m eval.run --config eval/configs/example.yaml --agent noop      # every task must FAIL
python -m eval.run --config eval/configs/example.yaml --agent reference # every task must PASS
python -m eval.run --config eval/configs/example.yaml --task fix_median # one task
```

Each run writes `eval/results/<run_id>/` containing `results.csv`, `results.md` and `meta.json`. The metadata records the model name and Ollama digest, the full config and its hash, the date, the code commit, and the Python version and platform. Model requests use the config's `params` (default `temperature: 0, seed: 42`) so reruns are comparable.

## Adding a task

Create `eval/tasks/<id>/` with these files:

| Path | Purpose |
|---|---|
| `task.yaml` | `id`, `class`, `instruction`, `check`. The full format is in the docstring of [tasks.py](tasks.py). |
| `repo/` | The starting snapshot. The agent works on a fresh copy of it each run. |
| `check/` | Hidden files copied in **after** the agent finishes, then `check.command` runs. Put a copy of any test file the agent shouldn't edit here too; the copy overwrites the agent's version. |
| `solution/` | Your reference fix, copied over the repo by `--agent reference`. |

`class` must be one of: `boilerplate`, `small_edit`, `explain`, `tests`, `debug`, `multi_file_refactor`, `long_context`.

A task is ready when `--agent noop` fails it and `--agent reference` passes it. `pytest eval/` checks this automatically for the 5 starter tasks only.

Tips:
- Checks should test behaviour, not wording. For example, run hidden tests rather than comparing files.
- Check commands use `{python}` for the harness's interpreter. Snapshots should only need the standard library and pytest.
- Write instructions the way you would actually ask, not hand-tuned to one model.
- Evaluation auto-approves every action inside the temporary copy. Commands are still limited to the allowlist. Only run tasks you trust.
