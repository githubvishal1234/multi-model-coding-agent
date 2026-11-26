// Runs `python -m ferrule ... --json` and speaks its line protocol. No VS Code imports, so it
// can be tested with plain Node. Ferrule writes one JSON object per stdout line:
//   {"type": "event", "kind", "data"} | {"type": "approval", "id", "kind", "summary", "detail"}
//   | {"type": "result", "status", "answer", "steps", "usage", "model"}
// and reads {"id": n, "approved": true|false} on stdin for each approval.
const { spawn } = require("child_process");
const path = require("path");
const readline = require("readline");

function runFerrule({ command, args, cwd, env, onEvent, onApproval, onLog }) {
  const child = spawn(command, args, {
    cwd,
    env: { ...withPythonFirst(process.env, command), ...env, PYTHONIOENCODING: "utf-8" },
    windowsHide: true,
  });
  let result = null;
  const lines = readline.createInterface({ input: child.stdout });
  lines.on("line", async (line) => {
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      if (onLog) onLog(line + "\n"); // not protocol output (e.g. a library warning)
      return;
    }
    if (msg.type === "event") {
      if (onEvent) onEvent(msg);
    } else if (msg.type === "approval") {
      let approved = false;
      try {
        approved = (await onApproval(msg)) === true; // anything but an explicit yes rejects
      } catch {
        approved = false;
      }
      if (child.stdin.writable) child.stdin.write(JSON.stringify({ id: msg.id, approved }) + "\n");
    } else if (msg.type === "result") {
      result = msg;
      child.stdin.end(); // no more approvals can follow

    } else if (onLog) {
      onLog(line + "\n");
    }
  });
  child.stderr.on("data", (d) => onLog && onLog(d.toString()));
  const done = new Promise((resolve) => {
    child.on("error", (error) => resolve({ result: null, code: null, error }));
    child.on("close", (code) => resolve({ result, code, error: null }));
  });
  return { done, stop: () => child.kill() };
}

// Put the chosen interpreter's folder first on PATH, so the commands Ferrule runs
// ("python -m pytest", "python -m ...") use the same Python, not whatever PATH finds first.
function withPythonFirst(env, python) {
  if (!path.isAbsolute(python)) return { ...env };
  const key = Object.keys(env).find((k) => k.toUpperCase() === "PATH") || "PATH"; // "Path" on Windows
  return { ...env, [key]: path.dirname(python) + path.delimiter + (env[key] || "") };
}

module.exports = { runFerrule, withPythonFirst };
