import asyncio
import sqlite3

import pytest
from helpers import MockProvider, make_ctx, tool_reply
from pydantic import BaseModel

from ferrule.agent import Agent
from ferrule.config import Settings
from ferrule.events import ScriptedApprover
from ferrule.providers import Reply
from ferrule.safety import Redactor, is_read_only_sql, mark_private, withhold_private
from ferrule.tools import ToolCall, validate

pytest.importorskip("sqlalchemy")
from ferrule.tools.db import db_tools  # noqa: E402

# --- read-only check ---

@pytest.mark.parametrize("sql", [
    "SELECT * FROM users",
    "select name from users where note = 'drop table x; delete'",  # keywords inside a string
    "-- delete everything\nSELECT 1",
    "WITH a AS (SELECT 1 AS n) SELECT n FROM a;",
    "SELECT [update], [delete] FROM t WITH (NOLOCK)",  # bracketed identifiers, NOLOCK hint
    "SELECT id FROM t ORDER BY id OFFSET 5 ROWS",
])
def test_read_only_sql_allows_single_queries(sql):
    assert is_read_only_sql(sql)


@pytest.mark.parametrize("sql", [
    "UPDATE users SET name = 'x'",
    "SELECT 1; DROP TABLE users",
    "SELECT 1 DROP TABLE users",  # T-SQL batch without a semicolon
    "SELECT * INTO backup_users FROM users",
    "WITH a AS (SELECT 1) DELETE FROM users",
    "EXEC sp_who",
    "SELECT pg_terminate_backend(42)",
    "SELECT * FROM t FOR UPDATE",
    "",
])
def test_read_only_sql_blocks_writes_and_batches(sql):
    assert not is_read_only_sql(sql)


# --- private values ---

def test_withhold_private_replaces_marked_text_even_when_truncated():
    text = "2 rows\n" + mark_private("ann | 30\nbob | 41", "2 result rows") + "\ndone"
    out = withhold_private(text)
    assert "ann" not in out and out.startswith("2 rows\n[2 result rows withheld") and "done" in out
    cut = withhold_private("x " + mark_private("secret value", "1 result rows")[:-10])
    assert "secret" not in cut and cut.startswith("x [1 result rows withheld")


def test_settings_and_redactor_handle_db_urls():
    env = {"FERRULE_DB_MAIN": "mssql+pyodbc://sa:Pa55word!@localhost/app",
           "FERRULE_DB_WRITABLE": '["main"]', "FERRULE_DB_MAX_ROWS": "5"}
    s = Settings.from_env(env)
    assert s.databases == {"main": env["FERRULE_DB_MAIN"]}
    assert s.db_writable == ["main"] and s.db_max_rows == 5
    assert "Pa55word" not in repr(s) and "databases" not in s.model_dump()
    assert Redactor(env)("login failed, pw Pa55word!") == "login failed, pw [REDACTED]"


# --- tools on SQLite ---

@pytest.fixture
def db_settings(settings, tmp_path):
    path = tmp_path / "app.db"
    con = sqlite3.connect(path)
    con.executescript("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL);"
                      "INSERT INTO users (name) VALUES ('ann'), ('bob'), ('cy');")
    con.commit()
    con.close()
    return settings.model_copy(update={"databases": {"app": f"sqlite:///{path}"},
                                       "db_max_rows": 2}), path


def names(path):
    with sqlite3.connect(path) as con:
        return [r[0] for r in con.execute("SELECT name FROM users ORDER BY id")]


def db_call(settings, name, answers=(), **args):
    ctx, approver = make_ctx(settings, answers)
    tool, parsed = validate(db_tools(), ToolCall(name, args))
    return asyncio.run(tool.run(parsed, ctx)), approver


def test_schema_lists_tables_and_columns(db_settings):
    s, _ = db_settings
    assert db_call(s, "db_schema", db="app")[0].output == "main.users"
    out = db_call(s, "db_schema", db="app", table="users")[0].output
    assert "name TEXT NOT NULL" in out and "primary key: id" in out


def test_select_runs_without_approval_capped_and_private(db_settings):
    s, _ = db_settings
    r, approver = db_call(s, "run_sql", db="app", sql="SELECT id, name FROM users ORDER BY id")
    assert r.ok and not approver.requests
    assert r.output.startswith("2 rows (more than 2") and "columns: id | name" in r.output
    assert "1 | ann" in r.output and "cy" not in r.output
    assert "ann" not in withhold_private(r.output)  # hosted models never see the values


def test_write_on_read_only_connection_is_refused(db_settings):
    s, path = db_settings
    r, approver = db_call(s, "run_sql", [True, True], db="app", sql="DELETE FROM users")
    assert not r.ok and "read-only" in r.error and not approver.requests
    assert names(path) == ["ann", "bob", "cy"]


def test_write_commits_only_after_second_approval(db_settings):
    s, path = db_settings
    s = s.model_copy(update={"db_writable": ["app"]})
    sql = "UPDATE users SET name = 'ANN' WHERE id = 1"
    r, approver = db_call(s, "run_sql", [True, False], db="app", sql=sql)
    assert not r.ok and "rolled back (1 rows affected)" in r.error
    assert [q.kind for q in approver.requests] == ["run_sql", "run_sql_commit"]
    assert "1 rows affected" in approver.requests[1].summary
    assert names(path) == ["ann", "bob", "cy"]
    r, _ = db_call(s, "run_sql", [True, True], db="app", sql=sql)
    assert r.ok and r.output.startswith("committed on app: 1 rows affected")
    assert names(path) == ["ANN", "bob", "cy"]


def test_rejected_write_never_runs(db_settings):
    s, path = db_settings
    s = s.model_copy(update={"db_writable": ["app"]})
    r, approver = db_call(s, "run_sql", [False], db="app", sql="DELETE FROM users")
    assert not r.ok and len(approver.requests) == 1 and names(path) == ["ann", "bob", "cy"]


def test_errors_are_private_and_unknown_db_is_named(db_settings):
    s, _ = db_settings
    r, _ = db_call(s, "run_sql", db="app", sql="SELECT nope FROM users")
    assert r.error.startswith("OperationalError: ") and "nope" not in withhold_private(r.error)
    r, _ = db_call(s, "run_sql", db="other", sql="SELECT 1")
    assert r.error == "unknown database 'other'. Configured: app"


# --- load_csv ---

@pytest.fixture
def csv_settings(db_settings, ws):
    s, path = db_settings
    with sqlite3.connect(path) as con:
        con.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, sku TEXT NOT NULL UNIQUE, "
                    "price REAL, added DATE)")
    (ws / "new.csv").write_text("SKU,Price,Added\nKB-1,3499.00,2026-11-01\n\nMS-2,,2026-11-02\n",
                                encoding="utf-8-sig")  # BOM and a blank line, as Excel writes
    return s.model_copy(update={"db_writable": ["app"]}), path


def products(path):
    with sqlite3.connect(path) as con:
        return con.execute("SELECT sku, price, added FROM products ORDER BY sku").fetchall()


def test_load_csv_inserts_after_one_approval_and_shows_no_values(csv_settings):
    s, path = csv_settings
    cols = {"SKU": "sku", "Price": "price", "Added": "added"}
    r, approver = db_call(s, "load_csv", [True], db="app", path="new.csv", table="products",
                          columns=cols)
    assert r.ok and r.output.startswith("committed: 2 rows inserted into products")
    assert "KB-1" not in r.output and "3499" not in r.output  # the model never sees values
    [req] = approver.requests
    assert req.kind == "load_csv" and "commit 2 rows" in req.summary
    assert "KB-1 | 3499.00 | 2026-11-01" in req.detail  # the user sees a preview
    assert products(path) == [("KB-1", 3499.0, "2026-11-01"), ("MS-2", None, "2026-11-02")]


def test_load_csv_declined_rolls_back(csv_settings):
    s, path = csv_settings
    r, _ = db_call(s, "load_csv", [False], db="app", path="new.csv", table="products",
                   columns={"SKU": "sku"})
    assert not r.ok and "rolled back 2 rows" in r.error and products(path) == []


def test_load_csv_reports_mapping_problems_without_values(csv_settings):
    s, _ = csv_settings
    # No mapping: headers match column names case-insensitively, so it reaches the commit step.
    r, approver = db_call(s, "load_csv", db="app", path="new.csv", table="products")
    assert "rolled back 2 rows" in r.error
    assert "SKU -> sku, Price -> price, Added -> added" in approver.requests[0].detail
    r, approver = db_call(s, "load_csv", db="app", path="new.csv", table="products",
                   columns={"Cost": "price", "SKU": "code"})
    assert not approver.requests
    assert "no CSV column 'Cost'" in r.error and "no table column 'code'" in r.error
    assert "CSV headers: SKU, Price, Added" in r.error and "KB-1" not in r.error


def test_load_csv_counts_empty_cells_for_not_null_columns(csv_settings, ws):
    s, path = csv_settings
    (ws / "gaps.csv").write_text("sku,price\nA-1,1\n,2\n,3\n")
    r, approver = db_call(s, "load_csv", [True], db="app", path="gaps.csv", table="products")
    assert r.error.startswith("table column 'sku' does not allow NULL, but 2 rows have an "
                              "empty 'sku'.")
    assert not approver.requests and products(path) == []


def test_load_csv_refuses_read_only_db_and_ragged_rows(csv_settings, ws):
    s, path = csv_settings
    ro = s.model_copy(update={"db_writable": []})
    assert "read-only" in db_call(ro, "load_csv", db="app", path="new.csv",
                                  table="products")[0].error
    (ws / "bad.csv").write_text("sku,price\nA-1,1\nA-2\n")
    r, _ = db_call(s, "load_csv", db="app", path="bad.csv", table="products")
    assert r.error == "line 3 has 1 fields but the header has 2" and products(path) == []


def test_csv_contents_are_private_when_databases_are_configured(csv_settings, ws):
    s, _ = csv_settings
    ctx, _ = make_ctx(s)
    from helpers import call
    out = call(ctx, "read_file", path="new.csv").output
    assert "KB-1" in out and "KB-1" not in withhold_private(out)
    assert call(ctx, "search_repo", pattern="KB-1").output == (
        "[not searched: the contents of 1 private data files, e.g. new.csv; use load_csv + "
        "run_sql for data]\nno matches")
    plain, _ = make_ctx(s.model_copy(update={"databases": {}}))
    assert call(plain, "search_repo", pattern="KB-1").output.startswith("new.csv:2:")


def test_agent_offers_db_tools_and_stays_local_after_reading_rows(db_settings):
    s, _ = db_settings
    s = s.model_copy(update={"supports_tools": False})

    class LocalRouted(MockProvider):
        kept_local = False

        def keep_local(self):
            self.kept_local = True

    provider = LocalRouted(tool_reply("run_sql", db="app", sql="SELECT name FROM users"),
                           Reply(content="There are users."))
    agent = Agent(provider, s, ScriptedApprover(default=True))
    asyncio.run(agent.run("how many users?"))
    first = provider.calls[0]["messages"][1]["content"]
    assert "Databases (use db_schema and run_sql): app (read-only)" in first
    assert {"db_schema", "run_sql"} <= set(agent.tools) and provider.kept_local


# --- crash and privacy fixes from the big-data tests ---

def test_load_csv_messy_files_return_errors_and_encodings_load(csv_settings, ws):
    s, path = csv_settings
    (ws / "old_excel.csv").write_bytes("sku,price\nCAFÉ-1,1\nNIÑO-2,2\n".encode("cp1252"))
    r, _ = db_call(s, "load_csv", [True], db="app", path="old_excel.csv", table="products")
    assert not r.ok and "encoding='cp1252'" in r.error and products(path) == []
    r, _ = db_call(s, "load_csv", [True], db="app", path="old_excel.csv", table="products",
                   encoding="cp1252")
    assert r.ok and [p[0] for p in products(path)] == ["CAFÉ-1", "NIÑO-2"]

    # Excel "Unicode Text": UTF-16 with a BOM, tab-separated
    (ws / "unicode.txt").write_text("sku\tprice\nU-1\t3\n", encoding="utf-16")
    r, _ = db_call(s, "load_csv", [True], db="app", path="unicode.txt", table="products")
    assert r.error == r"the header looks tab-separated: retry with delimiter='\t'"
    r, _ = db_call(s, "load_csv", [True], db="app", path="unicode.txt", table="products",
                   delimiter="\t")
    assert r.ok and ("U-1", 3.0, None) in products(path)

    (ws / "book.xlsx").write_bytes(b"PK\x03\x04" + b"\0" * 100)
    r, _ = db_call(s, "load_csv", db="app", path="book.xlsx", table="products")
    assert "is an Excel workbook" in r.error and "CSV UTF-8" in r.error

    (ws / "long.csv").write_text("sku,price\n" + "L" * 200_000 + ",1\n")
    r, _ = db_call(s, "load_csv", [True], db="app", path="long.csv", table="products")
    assert r.ok  # over Python's default 131,072-char field limit

    (ws / "dupes.csv").write_text("sku,price,price\nD-1,1,2\n")
    r, _ = db_call(s, "load_csv", db="app", path="dupes.csv", table="products")
    assert r.error.startswith("duplicate header names: price.")


def test_run_tool_turns_any_tool_exception_into_an_error(settings, db_settings):
    from ferrule.tools import Tool, ToolResult, run_tool

    class Boom(Tool):
        name = "boom"
        description = "raises"

        class Args(BaseModel):
            pass

        async def run(self, a, ctx):
            raise UnicodeDecodeError("utf-8", b"\xe9 secret", 0, 1, "invalid byte")

    for s, hosted_sees_secret in ((settings, True), (db_settings[0], False)):
        ctx, _ = make_ctx(s)
        r = asyncio.run(run_tool(Boom(), Boom.Args(), ctx))
        assert isinstance(r, ToolResult) and not r.ok
        assert r.error.startswith("boom failed: UnicodeDecodeError: ")
        assert ("invalid byte" in withhold_private(r.error)) == hosted_sees_secret


def test_private_files_cover_data_formats_and_user_globs(db_settings, ws):
    from helpers import call
    s, _ = db_settings
    (ws / "events.jsonl").write_text('{"user": "ann"}\n')
    (ws / "README.md").write_text("ann is the maintainer\n")
    (ws / "data").mkdir()
    (ws / "data" / "people.txt").write_text("ann|30\n")
    ctx, _ = make_ctx(s)
    assert "ann" not in withhold_private(call(ctx, "read_file", path="events.jsonl").output)
    assert "ann" in withhold_private(call(ctx, "read_file", path="README.md").output)
    assert "ann" in withhold_private(call(ctx, "read_file", path="data/people.txt").output)
    ctx, _ = make_ctx(s.model_copy(update={"private_files": [*s.private_files, "data/*"]}))
    assert "ann" not in withhold_private(call(ctx, "read_file", path="data/people.txt").output)


def test_search_says_when_a_big_file_was_only_partly_searched(settings, ws):
    from helpers import call
    (ws / "big.log").write_text("x" * 2_100_000 + "\nNEEDLE\n")
    ctx, _ = make_ctx(settings)
    out = call(ctx, "search_repo", pattern="NEEDLE").output
    assert out == "[only the first 2 MB was searched in 1 files, e.g. big.log]\nno matches"


def test_read_file_refuses_files_over_the_size_limit(settings, ws, monkeypatch):
    from helpers import call
    monkeypatch.setattr("ferrule.tools.files.MAX_READ_BYTES", 1000)
    (ws / "huge.csv").write_text("a,b\n" * 1000)
    ctx, _ = make_ctx(settings)
    r = call(ctx, "read_file", path="huge.csv")
    assert not r.ok and "read_file only reads files up to" in r.error and "load_csv" in r.error


def test_workspace_script_output_is_private_but_other_commands_are_not(db_settings, ws):
    import sys as _sys

    from helpers import call
    s, _ = db_settings
    s = s.model_copy(update={"allowlist": {"python": ["-m"]}})
    (ws / "dump.py").write_text("print('ann,30')\n")
    ctx, approver = make_ctx(s, default=True)
    # Run the module with this interpreter: argv[0] must be "python" for the allowlist.
    r = call(ctx, "run_command", argv=["python", "-m", "dump"])
    if not r.ok and "not found on PATH" in (r.error or ""):
        pytest.skip(f"no python on PATH (tests run with {_sys.executable})")
    assert "ann,30" in r.output and "ann" not in withhold_private(r.output)
    assert "kept from hosted models" in approver.requests[0].summary
    r = call(ctx, "run_command", argv=["python", "-m", "platform"])  # not a workspace script
    assert withhold_private(r.output) == r.output


def test_fixed_model_redacts_and_withholds_only_when_not_local(settings):
    from ferrule.router import build_provider, is_local_url
    assert is_local_url("http://127.0.0.1:11434/v1") and not is_local_url("https://x.ai/v1")
    for url, local in (("http://127.0.0.1:11434/v1", True), ("https://api.example.com/v1", False)):
        s = settings.model_copy(update={"model": "m", "base_url": url})
        p = asyncio.run(build_provider(s, "task"))
        assert p.is_local == local and (p.outbound is None) == local
        if not local:
            assert "ann" not in p.outbound(mark_private("ann | 30", "1 result rows"))
