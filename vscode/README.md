# Ferrule for VS Code

Runs the Ferrule coding agent on the folder open in VS Code. You type a task, watch the agent's progress in the **Ferrule** output panel, and approve or reject every file edit, command and database change in a dialog.

The extension has no AI of its own and needs no account. It starts `python -m ferrule run "<task>" --workspace <folder> --json` and talks to it over stdin/stdout: Ferrule writes one JSON object per line, and the extension answers each approval. Models, API keys and safety rules all come from your Ferrule setup.

## Setup

1. Install the extension (see "Build and install" below).
2. Open VS Code settings (`Ctrl+,`), search for "Ferrule", and set:
   - **Ferrule: Python Path**: the Python that has Ferrule's dependencies, e.g. `D:\GenAI_projects\Multi-Model Coding Agent\.venv\Scripts\python.exe`
   - **Ferrule: Ferrule Dir**: the folder that contains the `ferrule` package and your `.env` with the API keys and `FERRULE_DB_*` lines. Ferrule runs from here.
   - **Ferrule: Local Only** (optional): never send code to hosted models.
3. Open the folder you want Ferrule to work on.

The extension puts the chosen Python's folder first on PATH for Ferrule, so the tests it runs (`python -m pytest`) use that same Python.

## Commands

Open the Command Palette with `Ctrl+Shift+P`:

| Command | What it does |
|---|---|
| Ferrule: Run Task | Asks for a task and runs it. Unsaved files are saved first. |
| Ferrule: Plan Task | Ferrule proposes a plan, and nothing runs until you approve it. |
| Ferrule: Stop | Stops the running task. |
| Ferrule: Undo Last Run (files only) | Restores files changed by the last run. Database changes are not undone. |
| Ferrule: Check Setup | Runs `ferrule doctor`: hardware, local models, which hosted providers work. |

When Ferrule wants to change something, a dialog shows the summary and the start of the diff or SQL. The full text is in the Ferrule output panel. Anything other than **Approve**, including closing the dialog, rejects the change.

## Build and install

```powershell
cd vscode
node --test test/protocol.test.js          # protocol tests, no Python or model needed
npx --yes @vscode/vsce@3 package --skip-license --allow-missing-repository
code --install-extension ferrule-0.1.0.vsix
```

To try it without installing, open the `vscode` folder in VS Code and press `F5`. That opens an Extension Development Host window with the extension loaded.

## Limits

- One task at a time. In a multi-root workspace, the first folder is used.
- The protocol is one JSON object per line. It's documented at the top of `ferrule-process.js`, and Ferrule's side is in `ferrule/cli.py` (`--json`).
