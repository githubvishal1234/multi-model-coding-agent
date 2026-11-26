"""db_schema, run_sql and load_csv: database access through SQLAlchemy
(extra: pip install -e ".[db]").

Connections come from FERRULE_DB_<NAME> URLs. A single SELECT/WITH query runs without approval
inside a transaction that is always rolled back. Anything else needs a connection listed in
FERRULE_DB_WRITABLE and two approvals: one to run it inside a transaction, one to commit it
after the user has seen how many rows changed. Row values and database errors are marked
private, so they never reach hosted models unless FERRULE_DB_ROWS_TO_HOSTED=true.
"""

import csv
import re

from pydantic import BaseModel, Field

from ferrule.events import ApprovalRequest
from ferrule.safety import is_read_only_sql, mark_private
from ferrule.tools import Tool, ToolContext, ToolResult

CELL_CHARS = 200
MAX_CSV_ROWS = 100_000
MAX_FIELD_CHARS = 10_000_000  # per CSV field (long text, JSON or base64 cells)
COLLATE_RE = re.compile(r' COLLATE "[^"]*"')  # SQL Server repeats it on every text column
SYSTEM_SCHEMAS = {"information_schema", "sys", "guest", "pg_catalog", "pg_toast", "mysql",
                  "performance_schema"}
NOT_INSTALLED = 'database support is not installed: pip install -e ".[db]"'
_engines: dict[str, object] = {}  # URL -> Engine, so pooled connections are reused


class DbError(Exception):
    """A problem whose message is safe to show any model (no row values)."""


def _engine(ctx: ToolContext, name: str):
    url = ctx.settings.databases.get(name.lower())
    if url is None:
        names = ", ".join(sorted(ctx.settings.databases)) or "none configured"
        raise DbError(f"unknown database '{name}'. Configured: {names}")
    if url not in _engines:
        try:
            from sqlalchemy import create_engine
            _engines[url] = create_engine(url, pool_pre_ping=True)
        except ImportError as e:  # sqlalchemy itself, or the driver (e.g. pyodbc)
            raise DbError(f"{NOT_INSTALLED} ({e})") from None
    return _engines[url]


def _private(ctx: ToolContext, text: str, label: str) -> str:
    return text if ctx.settings.db_rows_to_hosted else mark_private(text, label)


def _error(ctx: ToolContext, e: Exception) -> ToolResult:
    # Driver messages can quote row values ("converting the varchar value 'Ann' ..."): private.
    detail = str(getattr(e, "orig", None) or e)
    return ToolResult(ok=False, error=f"{type(e).__name__}: "
                      f"{_private(ctx, detail, 'database error message')}\n"
                      "Use db_schema to check table and column names.")


def _cell(v) -> str:
    s = "NULL" if v is None else str(v).replace("\r", " ").replace("\n", " ")
    return s if len(s) <= CELL_CHARS else s[:CELL_CHARS] + "..."


def _rows(ctx: ToolContext, result) -> str:
    """Column names (schema, always shown) and up to db_max_rows rows (private)."""
    limit = ctx.settings.db_max_rows
    cols = list(result.keys())
    rows = result.fetchmany(limit + 1)
    result.close()
    shown = rows[:limit]
    more = f" (more than {limit}; narrow the query with WHERE or TOP/LIMIT)" if len(rows) > limit \
        else ""
    table = "\n".join(" | ".join(_cell(v) for v in r) for r in shown)
    return (f"{len(shown)} rows{more}\ncolumns: {' | '.join(cols)}\n"
            + _private(ctx, table, f"{len(shown)} result rows"))


class DbSchema(Tool):
    name = "db_schema"
    description = ("List the tables and views of a configured database, or with "
                   "table='schema.name' show its columns, primary key, foreign keys and indexes.")
    read_only = True

    class Args(BaseModel):
        db: str
        table: str | None = None

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        try:
            engine = _engine(ctx, a.db)
            from sqlalchemy import inspect
            from sqlalchemy.exc import SQLAlchemyError
        except DbError as e:
            return ToolResult(ok=False, error=str(e))
        try:
            insp = inspect(engine)
            if a.table is None:
                names = []
                for sch in insp.get_schema_names():
                    if sch.lower() in SYSTEM_SCHEMAS or sch.lower().startswith(("db_", "pg_")):
                        continue
                    names += [f"{sch}.{t}" for t in insp.get_table_names(schema=sch)
                              if not t.startswith("#")]  # SQL Server temp tables
                    names += [f"{sch}.{v} (view)" for v in insp.get_view_names(schema=sch)]
                return ToolResult(ok=True, output="\n".join(names) or "no tables")
            schema, _, table = a.table.rpartition(".")
            schema = schema or None
            lines = [f"{c['name']} {COLLATE_RE.sub('', str(c['type']))}"
                     f"{'' if c.get('nullable', True) else ' NOT NULL'}"
                     for c in insp.get_columns(table, schema=schema)]
            pk = insp.get_pk_constraint(table, schema=schema).get("constrained_columns")
            if pk:
                lines.append(f"primary key: {', '.join(pk)}")
            for fk in insp.get_foreign_keys(table, schema=schema):
                ref = ".".join(p for p in (fk.get("referred_schema"), fk["referred_table"]) if p)
                lines.append(f"foreign key: {', '.join(fk['constrained_columns'])} -> "
                             f"{ref}({', '.join(fk['referred_columns'])})")
            for ix in insp.get_indexes(table, schema=schema):
                unique = "unique " if ix.get("unique") else ""
                cols = ", ".join(c for c in ix.get("column_names", []) if c)
                lines.append(f"{unique}index {ix['name']}: {cols}")
            return ToolResult(ok=True, output="\n".join(lines))
        except SQLAlchemyError as e:
            return _error(ctx, e)


class RunSql(Tool):
    name = "run_sql"
    description = ("Run SQL on a configured database. A single SELECT or WITH query runs right "
                   "away and returns its rows. Anything else (INSERT, UPDATE, DELETE, CREATE, "
                   "ALTER, DROP, EXEC, several statements) needs a writable database and the "
                   "user's approval; it runs in a transaction and is committed only if the user "
                   "approves after seeing the row count. Do not use GO separators.")

    class Args(BaseModel):
        db: str
        sql: str = Field(min_length=1)

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        try:
            engine = _engine(ctx, a.db)
            from sqlalchemy.exc import SQLAlchemyError
        except DbError as e:
            return ToolResult(ok=False, error=str(e))
        # ponytail: SQL runs on the event-loop thread, which keeps each connection on one
        # thread across the approval await. A slow query blocks until the database returns.
        try:
            if is_read_only_sql(a.sql):
                with engine.connect() as conn:
                    try:
                        result = conn.exec_driver_sql(a.sql)  # raw SQL: no ':name' bind parsing
                        out = _rows(ctx, result) if result.returns_rows else "no rows returned"
                    finally:
                        conn.rollback()
                return ToolResult(ok=True, output=out)
            return await self._write(engine, a, ctx)
        except SQLAlchemyError as e:
            return _error(ctx, e)

    async def _write(self, engine, a: Args, ctx: ToolContext) -> ToolResult:
        if not _writable(ctx, a.db):
            return ToolResult(ok=False, error=(
                f"'{a.db}' is read-only: only a single SELECT or WITH query can run on it, and "
                "this statement may change data. Rewrite it as one SELECT, or ask the user to "
                f"add '{a.db}' to FERRULE_DB_WRITABLE."))
        if not await ctx.approve(ApprovalRequest(
                "run_sql", f"run SQL on {a.db} inside a transaction (you will be asked again "
                "before it is committed)", a.sql)):
            return ToolResult(ok=False, error="the user rejected running this SQL")
        with engine.connect() as conn:
            try:
                result = conn.exec_driver_sql(a.sql)
                count = result.rowcount
                rows = "\n" + _rows(ctx, result) if result.returns_rows else ""
                changed = f"{count} rows affected" if count >= 0 else \
                    "the driver did not report a row count"
                if not await ctx.approve(ApprovalRequest(
                        "run_sql_commit", f"commit on {a.db}? {changed} (the transaction stays "
                        "open, holding its locks, until you answer)", a.sql)):
                    conn.rollback()
                    return ToolResult(ok=False, error=f"the user did not commit; rolled back "
                                                      f"({changed})")
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
        return ToolResult(ok=True, output=f"committed on {a.db}: {changed}. Note: ferrule undo "
                                          f"does not restore database changes.{rows}")


def _writable(ctx: ToolContext, db: str) -> bool:
    return db.lower() in {d.lower() for d in ctx.settings.db_writable}


class LoadCsv(Tool):
    name = "load_csv"
    description = ("Insert the rows of a CSV file in the workspace into a table of a writable "
                   "database. The file's values never pass through you: you only choose the "
                   "table and, if the header names differ from the column names, columns = "
                   "{csv header: table column}. The first row must be the header. Empty cells "
                   "become NULL. All rows go in one transaction, committed only if the user "
                   "approves. Don't read the file with read_file. encoding: leave it out for "
                   "UTF-8; use 'cp1252' for files from older Excel versions.")

    class Args(BaseModel):
        db: str
        path: str
        table: str
        columns: dict[str, str] | None = None
        delimiter: str = Field(",", min_length=1, max_length=1)
        encoding: str | None = None  # None: UTF-8, or UTF-16 if the file starts with a BOM

    async def run(self, a: Args, ctx: ToolContext) -> ToolResult:
        try:
            engine = _engine(ctx, a.db)
            from sqlalchemy import MetaData, Table, column, insert, table
            from sqlalchemy.exc import SQLAlchemyError
        except DbError as e:
            return ToolResult(ok=False, error=str(e))
        if not _writable(ctx, a.db):
            return ToolResult(ok=False, error=f"'{a.db}' is read-only; ask the user to add it "
                                              "to FERRULE_DB_WRITABLE.")
        path = ctx.resolve(a.path)
        if not path.is_file():
            return ToolResult(ok=False, error=f"not a file: {a.path}")
        with open(path, "rb") as f:
            head = f.read(4)
        if head.startswith((b"PK\x03\x04", b"\xd0\xcf\x11\xe0")):  # .xlsx (zip), .xls (OLE)
            return ToolResult(ok=False, error=(
                f"{a.path} is an Excel workbook, not a CSV. Ask the user to save it from Excel "
                "with 'Save As' -> 'CSV UTF-8 (Comma delimited)'."))
        # UTF-16 with a BOM is Excel's "Unicode Text"; otherwise UTF-8 (with or without BOM).
        encoding = a.encoding or ("utf-16" if head[:2] in (b"\xff\xfe", b"\xfe\xff")
                                  else "utf-8-sig")
        csv.field_size_limit(MAX_FIELD_CHARS)  # Python's default is 131,072 chars per field
        # ponytail: the whole file is read into memory; MAX_CSV_ROWS bounds it. Stream in
        # batches if bigger loads are needed.
        reader = None
        try:
            with open(path, encoding=encoding, newline="") as f:
                reader = csv.reader(f, delimiter=a.delimiter)
                header = [h.strip() for h in next(reader, [])]
                rows = []
                for r in reader:
                    if not any(cell.strip() for cell in r):
                        continue  # blank line
                    if len(r) != len(header):
                        return ToolResult(ok=False, error=f"line {reader.line_num} has {len(r)} "
                                          f"fields but the header has {len(header)}")
                    if len(rows) == MAX_CSV_ROWS:
                        return ToolResult(ok=False, error=f"more than {MAX_CSV_ROWS} rows; "
                                                          "split the file")
                    rows.append(r)
        except UnicodeDecodeError as e:
            return ToolResult(ok=False, error=(
                f"{a.path} is not valid {encoding} (bad byte at offset {e.start}). Files from "
                "older Excel versions are usually Windows-1252: retry with encoding='cp1252'."))
        except LookupError:
            return ToolResult(ok=False, error=f"unknown encoding '{encoding}'")
        except csv.Error as e:  # e.g. a NUL byte in a quoted field, or a field over the limit
            where = f" at line {reader.line_num}" if reader else ""
            return ToolResult(ok=False, error=f"{a.path} is not a readable CSV{where}: {e}")
        if not header or not rows:
            return ToolResult(ok=False, error=f"{a.path} has no header or no data rows")
        if len(header) == 1 and a.delimiter != "\t" and "\t" in header[0]:
            return ToolResult(ok=False, error="the header looks tab-separated: retry with "
                                              "delimiter='\\t'")
        dupes = sorted({h for h in header if header.count(h) > 1})
        if dupes:  # columns is keyed by header name, so a second copy could never be loaded
            return ToolResult(ok=False, error=f"duplicate header names: {', '.join(dupes)}. Ask "
                              "the user to rename them in the file.")
        schema, _, name = a.table.rpartition(".")
        try:
            target = Table(name, MetaData(), schema=schema or None, autoload_with=engine)
        except SQLAlchemyError as e:
            return _error(ctx, e)
        cols = {c.name.lower(): c for c in target.columns}
        mapping = a.columns or {h: h for h in header}
        problems = [f"no CSV column '{h}'" for h in mapping if h not in header]
        problems += [f"no table column '{c}'" for c in mapping.values() if c.lower() not in cols]
        problems += [f"'{c}' is an identity column (the database fills it); leave it out"
                     for c in mapping.values()
                     if c.lower() in cols and cols[c.lower()].identity is not None]
        if problems:
            names = ", ".join(c.name for c in cols.values())
            return ToolResult(ok=False, error="; ".join(problems) + f".\nCSV headers: "
                              f"{', '.join(header)}\nTable columns: {names}")
        pairs = [(header.index(h), cols[c.lower()].name) for h, c in mapping.items()]
        # Checked here because the database's own NULL error is private (it names values)
        # and a hosted model would only see "IntegrityError". Counts only, no values.
        for i, col in pairs:
            empty = sum(1 for r in rows if r[i] == "")
            if empty and not cols[col.lower()].nullable:
                default = " Its database default is not used for empty cells." \
                    if cols[col.lower()].server_default is not None else ""
                problems.append(f"table column '{col}' does not allow NULL, but {empty} rows "
                                f"have an empty '{header[i]}'.{default} Ask the user to fill "
                                "them in, or leave the column out of columns")
        if problems:
            return ToolResult(ok=False, error="\n".join(problems))
        records = [{col: (r[i] if r[i] != "" else None) for i, col in pairs} for r in rows]
        # Untyped columns: values go to the driver as text and the database converts them
        # (SQLAlchemy's own types would reject e.g. '2026-11-01' for a SQLite DATE column).
        stmt = insert(table(target.name, *[column(col) for _, col in pairs],
                            schema=target.schema))
        preview = "\n".join(" | ".join(_cell(v) for v in rec.values()) for rec in records[:3])
        detail = (f"file: {a.path}\ncolumns: "
                  + ", ".join(f"{h} -> {cols[c.lower()].name}" for h, c in mapping.items())
                  + f"\nfirst rows:\n{preview}")
        try:
            with engine.connect() as conn:
                try:
                    for i in range(0, len(records), 1000):
                        conn.execute(stmt, records[i:i + 1000])
                    if not await ctx.approve(ApprovalRequest(
                            "load_csv", f"commit {len(records)} rows from {a.path} into "
                            f"{a.table} on {a.db}? (the transaction stays open, holding its "
                            "locks, until you answer)", detail)):
                        conn.rollback()
                        return ToolResult(ok=False, error=f"the user did not commit; rolled "
                                                          f"back {len(records)} rows")
                    conn.commit()
                except BaseException:
                    conn.rollback()
                    raise
        except SQLAlchemyError as e:
            return _error(ctx, e)
        return ToolResult(ok=True, output=f"committed: {len(records)} rows inserted into "
                          f"{a.table} on {a.db} (columns: {', '.join(c for _, c in pairs)}). "
                          "ferrule undo does not restore database changes.")


def db_tools() -> dict[str, Tool]:
    return {t.name: t for t in (DbSchema(), RunSql(), LoadCsv())}
