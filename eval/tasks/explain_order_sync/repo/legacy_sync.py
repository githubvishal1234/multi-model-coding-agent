"""Old sync job. Replaced by sync.py; still here for the data migration notes."""

RETRIES = 5


def legacy_sync(client, store):
    page = 1
    while page < 100:
        for _ in range(RETRIES):
            try:
                orders = client.get_orders(page=page)
                break
            except Exception:
                orders = None
        if orders is None:  # give up on this page and move on
            page += 1
            continue
        for order in orders:
            if order["status"] != "canceled":
                store.save(order)
        page += 1
