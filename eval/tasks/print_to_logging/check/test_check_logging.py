import ast
import logging
import pathlib

from importer import parse_rows

LINES = ["a,1", "bad line", "b, 2", "c,x"]


def test_log_records(caplog, capsys):
    caplog.set_level(logging.DEBUG)
    assert parse_rows(LINES) == [("a", 1), ("b", 2)]
    records = [(r.name, r.levelname, r.getMessage()) for r in caplog.records]
    assert records == [
        ("importer", "INFO", "importing 4 lines"),
        ("importer", "WARNING", "skipping line 2: 'bad line'"),
        ("importer", "WARNING", "skipping line 4: 'c,x'"),
        ("importer", "INFO", "imported 2 rows"),
    ]
    assert capsys.readouterr().out == ""


def test_no_print_and_no_logging_config():
    src = pathlib.Path("importer.py").read_text()
    calls = [n.func for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call)]
    assert not any(isinstance(f, ast.Name) and f.id == "print" for f in calls), "print() left"
    assert "basicConfig" not in src and "addHandler" not in src
