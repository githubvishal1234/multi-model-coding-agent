from daily import build_daily_report

ORDERS = [{"day": "mon", "total": 10.0}, {"day": "mon", "total": 25.5}, {"day": "tue", "total": 4.0}]


def test_report_for_a_busy_day():
    assert build_daily_report(ORDERS, "mon") == {"day": "mon", "orders": 2, "aov": 17.75}
