from app import run_all
from registry import REPORTS


def test_run_all_lists_every_service():
    raw = {"orders": [{"key": " B ", "amount": 1}, {"key": "a", "amount": 2}, {"key": "", "amount": 9}]}
    out = run_all(raw)
    assert [r["key"] for r in out["orders"]] == ["a", "b"]
    assert len(out) == 18


def test_reports_registry():
    items = [{"key": "a", "amount": 1.5}, {"key": "b", "amount": 2.0}]
    for summarize in REPORTS.values():
        assert summarize(items) == {"count": 2, "total": 3.5}
