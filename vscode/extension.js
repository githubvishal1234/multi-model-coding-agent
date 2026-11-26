// Ferrule for VS Code: run a task on the open folder, watch it in the "Ferrule" output panel,
// and approve or reject every file edit, command and database change in a dialog.
const vscode = require("vscode");
const { spawn } = require("child_process");
const { runFerrule, withPythonFirst } = require("./ferrule-process");

const MODAL_DETAIL_CHARS = 1500; // the full diff/SQL is always printed in the output panel
let output;
let current = null; // the running task, if any

function activate(context) {
  output = vscode.window.createOutputChannel("Ferrule");
  const reg = (id, fn) => context.subscriptions.push(vscode.commands.registerCommand(id, fn));
  reg("ferrule.run", () => startTask("run"));
  reg("ferrule.plan", () => startTask("plan"));
  reg("ferrule.undo", () => runPlain(["undo"]));
  reg("ferrule.doctor", () => runPlain(["doctor", "--no-speed-test", "--no-pull"]));
  reg("ferrule.stop", () => {
    if (!current) return vscode.window.showInformationMessage("Ferrule is not running a task.");
    current.stop();
    output.appendLine("\n[stopped by you]");
  });
  context.subscriptions.push(output);
}

function deactivate() {
  if (current) current.stop();
}

function settings() {
  const c = vscode.workspace.getConfiguration("ferrule");
  // ponytail: multi-root workspaces use the first folder; add a folder picker if needed.
  const folder = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
  if (!folder) {
    vscode.window.showErrorMessage("Ferrule: open a folder first; Ferrule works on that folder.");
    return null;
  }
  const ferruleDir = c.get("ferruleDir");
  if (!ferruleDir) {
    vscode.window
      .showErrorMessage("Ferrule: set 'ferrule.ferruleDir' to the folder with the ferrule package "
        + "and its .env, and 'ferrule.pythonPath' to its Python.", "Open Settings")
      .then((a) => a && vscode.commands.executeCommand("workbench.action.openSettings", "ferrule"));
    return null;
  }
  return { python: c.get("pythonPath") || "python", ferruleDir, folder: folder.uri.fsPath,
           localOnly: c.get("localOnly") };
}

async function startTask(command) {
  if (current) {
    return vscode.window.showWarningMessage("Ferrule is already running a task. "
      + "Use 'Ferrule: Stop' first.");
  }
  const s = settings();
  if (!s) return;
  const task = await vscode.window.showInputBox({
    prompt: command === "plan" ? "Task for Ferrule to plan first" : "Task for Ferrule",
    placeHolder: "e.g. add() in calc.py returns the wrong result, fix it",
    ignoreFocusOut: true,
  });
  if (!task) return;
  await vscode.workspace.saveAll(false); // Ferrule reads files from disk
  const args = ["-m", "ferrule", command, task, "--workspace", s.folder, "--json"];
  if (s.localOnly) args.push("--local-only");
  output.clear();
  output.show(true);
  output.appendLine(`> ${command}: ${task}\n  folder: ${s.folder}\n`);

  current = runFerrule({ command: s.python, args, cwd: s.ferruleDir, onEvent: showEvent,
                         onApproval: askApproval, onLog: (t) => output.append(t) });
  const status = vscode.window.setStatusBarMessage("$(sync~spin) Ferrule is working...");
  const { result, code, error } = await current.done;
  status.dispose();
  current = null;

  if (error) {
    return vscode.window.showErrorMessage(`Ferrule: could not start '${s.python}': ${error.message}`);
  }
  if (!result) {
    return vscode.window.showErrorMessage(`Ferrule exited (code ${code}) without a result. `
      + "See the Ferrule output panel.");
  }
  const tokens = result.usage && result.usage.total_tokens ? `, ${result.usage.total_tokens} tokens` : "";
  output.appendLine(`\n[${result.status}] steps=${result.steps}, model=${result.model}${tokens}`);
  const answer = (result.answer || "").slice(0, 400);
  if (result.status === "done") {
    vscode.window.showInformationMessage(`Ferrule finished: ${answer || "done"}`);
  } else {
    vscode.window.showWarningMessage(`Ferrule stopped (${result.status}): ${answer}`);
  }
}

function showEvent({ kind, data }) {
  switch (kind) {
    case "token":
      output.append(data.text);
      break;
    case "tool_call":
      output.appendLine(`\n-> ${data.tool} ${JSON.stringify(data.args).slice(0, 300)}`);
      break;
    case "tool_result":
      output.appendLine(`<- ${data.tool}: ${data.ok ? "ok" : "failed: " + data.error}`);
      break;
    case "routing":
      output.appendLine(`\n[model] ${data.chosen} (${data.reason})`);
      break;
    case "plan":
      output.appendLine(`\nPlan:\n${data.text}`);
      break;
    case "done":
      break;
    default:
      if (data && data.message) output.appendLine(`\n[${kind}] ${data.message}`);
  }
}

async function askApproval({ summary, detail }) {
  if (detail) output.appendLine(`\n--- approval needed: ${summary}\n${detail}\n---`);
  const shown = detail && detail.length > MODAL_DETAIL_CHARS
    ? detail.slice(0, MODAL_DETAIL_CHARS) + "\n... (full text in the Ferrule output panel)"
    : detail || undefined;
  const pick = await vscode.window.showWarningMessage(`Ferrule wants to: ${summary}`,
    { modal: true, detail: shown }, "Approve");
  output.appendLine(pick === "Approve" ? "[approved]" : "[rejected]");
  return pick === "Approve";
}

function runPlain(ferruleArgs) {
  const s = settings();
  if (!s) return;
  output.show(true);
  output.appendLine(`\n> ferrule ${ferruleArgs.join(" ")}`);
  const child = spawn(s.python, ["-m", "ferrule", ...ferruleArgs, "--workspace", s.folder],
    { cwd: s.ferruleDir, env: { ...withPythonFirst(process.env, s.python), PYTHONIOENCODING: "utf-8" },
      windowsHide: true });
  child.stdout.on("data", (d) => output.append(d.toString()));
  child.stderr.on("data", (d) => output.append(d.toString()));
  child.on("error", (e) => vscode.window.showErrorMessage(`Ferrule: ${e.message}`));
}

module.exports = { activate, deactivate };
