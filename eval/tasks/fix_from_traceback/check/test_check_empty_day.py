import pytest

from daily import build_daily_report
from metrics import average_order_value, order_count

ORDERS = [{"day": "mon", "total": 10.0}, {"day": "mon", "total": 25.5}]


def test_empty_day_report():
    assert build_daily_report(ORDERS, "sun") == {"day": "sun", "orders": 0, "aov": 0.0}


def test_root_cause_fixed_in_metrics():
    assert average_order_value([]) == 0.0


def test_normal_days_unchanged():
    assert build_daily_report(ORDERS, "mon") == {"day": "mon", "orders": 2, "aov": 17.75}
    assert average_order_value([{"total": 1.0}, {"total": 2.0}, {"total": 2.0}]) == 1.67
    assert order_count(ORDERS) == 2


def test_bad_data_is_not_silenced():
    with pytest.raises(KeyError):
        average_order_value([{"day": "mon"}])
