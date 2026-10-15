from orders import order_total
from report import summary


def test_order_total():
    assert order_total({"items": [{"price": 2.5, "qty": 2}], "tax": 0.1}) == 5.5


def test_summary():
    assert summary([[1, 2], [3]]) == "2 orders, 6.00 total"
