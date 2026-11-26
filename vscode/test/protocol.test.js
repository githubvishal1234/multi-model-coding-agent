// Tests the line protocol against a fake Ferrule (a Node script), so no Python or model is needed.
const test = require("node:test");
const assert = require("node:assert");
const path = require("path");
const { runFerrule, withPythonFirst } = require("../ferrule-process");

const FAKE = path.join(__dirname, "fake-ferrule.js");

function run(answer) {
  const events = [];
  const asked = [];
  const logs = [];
  const handle = runFerrule({
    command: process.execPath,
    args: [FAKE],
    cwd: __dirname,
    onEvent: (e) => events.push(e),
    onApproval: async (a) => {
      asked.push(a);
      if (answer instanceof Error) throw answer;
      return answer;
    },
    onLog: (t) => logs.push(t),
  });
  return handle.done.then((r) => ({ ...r, events, asked, logs }));
}

test("approve: events stream, the answer reaches Ferrule, result arrives", async () => {
  const r = await run(true);
  assert.strictEqual(r.code, 0);
  assert.deepStrictEqual(r.events.map((e) => e.kind), ["tool_call", "token"]);
  assert.strictEqual(r.asked.length, 1);
  assert.strictEqual(r.asked[0].summary, "create a.txt");
  assert.strictEqual(r.result.status, "done");
  assert.strictEqual(r.result.answer, "approved=true");
  assert.ok(r.logs.join("").includes("not json"));
});

test("reject and handler errors both send approved=false", async () => {
  assert.strictEqual((await run(false)).result.answer, "approved=false");
  assert.strictEqual((await run(new Error("dialog failed"))).result.answer, "approved=false");
  assert.strictEqual((await run("yes")).result.answer, "approved=false"); // only true approves
});

test("the chosen Python's folder goes first on PATH, whatever the key's case", () => {
  const py = path.resolve("/venv/Scripts/python.exe");
  const out = withPythonFirst({ Path: "A" + path.delimiter + "B", X: "1" }, py);
  assert.strictEqual(out.Path, path.dirname(py) + path.delimiter + "A" + path.delimiter + "B");
  assert.strictEqual(out.PATH, undefined);
  assert.strictEqual(out.X, "1");
  assert.deepStrictEqual(withPythonFirst({ PATH: "A" }, "python"), { PATH: "A" }); // bare name: unchanged
});

test("a missing interpreter is reported, not thrown", async () => {
  const handle = runFerrule({ command: "no-such-python-xyz", args: [], cwd: __dirname,
                              onApproval: async () => true });
  const r = await handle.done;
  assert.ok(r.error);
  assert.strictEqual(r.result, null);
});
