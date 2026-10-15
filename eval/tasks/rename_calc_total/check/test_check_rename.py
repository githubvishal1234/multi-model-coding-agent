import pathlib

import pricing
from orders import order_total
from report import summary


def test_renamed_without_alias():
    assert hasattr(pricing, "compute_total")
    assert not hasattr(pricing, "calc_total")


def test_old_name_gone_everywhere():
    for f in pathlib.Path(".").glob("*.py"):
        if not f.name.startswith("test_check"):
            assert "calc_total" not in f.read_text(), f.name


def test_behaviour_unchanged():
    assert order_total({"items": [{"price": 2.5, "qty": 2}], "tax": 0.1}) == 5.5
    assert summary([[1, 2], [3]]) == "2 orders, 6.00 total"
