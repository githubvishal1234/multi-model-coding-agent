// Behaves like `python -m ferrule run ... --json` for the protocol test.
const readline = require("readline");
const out = (o) => process.stdout.write(JSON.stringify(o) + "\n");

out({ type: "event", kind: "tool_call", data: { tool: "write_file", args: { path: "a.txt" } } });
process.stdout.write("not json: a library warning\n");
out({ type: "approval", id: 1, kind: "write_file", summary: "create a.txt", detail: "+hi" });
const rl = readline.createInterface({ input: process.stdin });
rl.once("line", (line) => {
  const answer = JSON.parse(line);
  const ok = answer.id === 1 && answer.approved === true;
  out({ type: "event", kind: "token", data: { text: "Done." } });
  out({ type: "result", status: "done", answer: `approved=${ok}`, steps: 2, usage: {}, model: "fake" });
  rl.close();
});
