from metrics import average_order_value, order_count


def build_daily_report(orders, day):
    """Summary of one day's orders for the morning email."""
    todays_orders = [o for o in orders if o["day"] == day]
    return {
        "day": day,
        "orders": order_count(todays_orders),
        "aov": average_order_value(todays_orders),
    }
