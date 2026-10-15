from pricing import calc_total


def order_total(order):
    prices = [item["price"] * item["qty"] for item in order["items"]]
    return calc_total(prices, order.get("tax", 0.0))
