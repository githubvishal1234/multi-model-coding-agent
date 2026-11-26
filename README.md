# Ferrule

> **Work in progress.** "Ferrule" is a working name. This README is a placeholder; the full version (architecture diagram, evaluation results, demo) comes when the project is finished.

Ferrule is a local coding agent that runs on **free models**, either local through [Ollama](https://ollama.com) or free hosted tiers, and aims to pick the best available model for each task. It reads and searches a repository, proposes edits as diffs, and runs commands and tests. Every change needs your approval.

## Status

| Phase | Area | State |
|---|---|---|
| 1–2 | Requirements, architecture, plan ([docs/](docs/)) | done |
| 3 | Agent core, tools, safety layer, CLI | done |
| 4 | Evaluation harness ([eval/](eval/)) | done; task set being written |
| 5 | Model router, hardware-aware model selection, hosted providers | done; hosted comparison needs API keys |
| 6 | Web lookup tool | planned |
| 7 | Local FastAPI service with streaming | planned (the VS Code extension uses `--json` over stdin/stdout instead) |
| 8 | VS Code extension ([vscode/](vscode/)) | first version: run, plan, stop, undo, approvals in dialogs |
| 9 | Security review and hardening | planned |
| 10 | Full evaluation, CI, documentation | planned |

## Quick start

Requires Python 3.12+ and Ollama with a coding model pulled (e.g. `ollama pull qwen2.5-coder:7b`).

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"     # on macOS/Linux: .venv/bin/python
.venv/Scripts/python -m ferrule run "Add a docstring to foo() in calc.py" --workspace path/to/project
```

- `ferrule doctor` shows your hardware, picks the largest local model that fits, measures its speed, and checks which hosted providers are configured.
- By default a router picks the model for each task: local first, escalating to free hosted models (if their API keys are set) when the local one keeps failing. Use `--local-only` to keep code on your machine, or `--model NAME` to fix one model.
- `ferrule plan "..."` proposes numbered steps and runs nothing until you approve them.
- `ferrule undo` restores the files changed by the last run.
- Add `--no-native-tools` for models without function calling.
- Settings are `FERRULE_*` environment variables; see [.env.example](.env.example).

## Databases

Ferrule can inspect and query databases, and change them with your approval, through [SQLAlchemy](https://www.sqlalchemy.org/). It has been tested on SQL Server Express. PostgreSQL, MySQL and SQLite use the same code but haven't been tested against a real server yet.

```bash
.venv/Scripts/python -m pip install -e ".[db]"     # SQLAlchemy + pyodbc (SQL Server)
```

Add one `FERRULE_DB_<NAME>` line per database to `.env` (see [.env.example](.env.example)). The agent then gets three tools:

- `db_schema` lists tables and views, or one table's columns, keys and indexes.
- `run_sql` runs SQL. A single `SELECT`/`WITH` query runs without approval and returns at most `FERRULE_DB_MAX_ROWS` rows. It runs inside a transaction that is always rolled back.
- Anything else needs the connection listed in `FERRULE_DB_WRITABLE`, plus two approvals. First you approve running it inside a transaction. Then you see how many rows changed and approve the commit. If you answer no, it's rolled back.
- `load_csv` inserts a CSV file from the workspace into a table on a writable connection, for example `ferrule run "Load new_products.csv into dbo.products"`. The model only picks the table and matches CSV headers to columns. Ferrule reads the file and inserts the rows itself, so the values never pass through the model. Before inserting, it checks for unknown columns, identity columns, rows with the wrong number of fields, and empty cells in `NOT NULL` columns. All rows go in one transaction (up to 100,000), and you approve one commit after seeing the column mapping and the first rows. Empty cells become `NULL`. The file needs a header row. UTF-8 is the default, and UTF-16 with a BOM (Excel's "Unicode Text") is detected automatically; older Excel exports need `encoding='cp1252'`. Duplicate header names, `.xlsx`/`.xls` workbooks and non-UTF-8 bytes are refused with a message saying what to do.

Things to know:

- **Row values never go to hosted models** (Groq, Claude and others). They only see table and column names and row counts. Query rows and database error messages are withheld, because errors can quote values. Only a local Ollama model sees the values, and once it has, the rest of that run stays local. While databases are configured, data files get the same treatment. `read_file` withholds their contents from hosted models, and `search_repo` doesn't search inside them, saying so in its result. Data files are `.csv`, `.tsv`, `.psv`, `.jsonl`, `.ndjson`, `.xlsx`, `.xls`, `.parquet`, `.csv.gz` and `.dat` by default; add your own globs with `FERRULE_PRIVATE_FILES`, for example a `data/*` folder of `.txt` exports. The output of a script the agent runs from your workspace (`python -m <your module>`) is withheld too, and its approval prompt says so. Values you type into the task itself are not withheld. Set `FERRULE_DB_ROWS_TO_HOSTED=true` only for test data.
- **Row counts are still sent**, as chosen ("table and column names and row counts"). A hosted model running many `SELECT ... WHERE` queries could learn something about values from "0 rows" vs "1 rows".
- **Big files:** `read_file` refuses files over 50 MB and returns at most 8,000 characters per call; `search_repo` searches the first 2 MB of each file and says when it stopped early. For data, use `load_csv` and `run_sql`.
- **The read-only check is a keyword check, not a SQL parser.** For real protection, connect read-only databases with a login that can only read (for example `db_datareader` on SQL Server).
- **`ferrule undo` does not restore database changes.** The commit approval is the last chance to say no.
- **A write's transaction stays open while it waits for your commit answer**, holding its locks.
- Statements that SQL Server refuses inside a transaction (`CREATE DATABASE`, `BACKUP`, `ALTER DATABASE`) fail. Run those yourself.

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
