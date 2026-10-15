import pricing


def summary(price_lists):
    totals = [pricing.compute_total(prices) for prices in price_lists]
    return f"{len(totals)} orders, {sum(totals):.2f} total"
