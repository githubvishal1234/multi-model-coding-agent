def order_count(orders):
    return len(orders)


def average_order_value(orders):
    """Mean order total, rounded to cents."""
    if not orders:
        return 0.0
    total = sum(o["total"] for o in orders)
    return round(total / len(orders), 2)
