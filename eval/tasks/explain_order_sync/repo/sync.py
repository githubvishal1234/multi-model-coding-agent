"""Order sync: copies new orders from the remote shop API into the local store."""

MAX_RETRIES = 2  # extra tries after the first request
SKIP_STATUSES = {"cancelled", "test"}


class Timeout(Exception):
    pass


def fetch_page(client, since, page):
    """Request one page of orders, retrying on timeouts."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.get_orders(since=since, page=page)
        except Timeout:
            if attempt == MAX_RETRIES:
                raise


def sync_orders(client, store, since):
    """Store every new order since `since`; return how many were stored."""
    stored = 0
    page = 1
    while True:
        orders = fetch_page(client, since, page)
        if not orders:
            return stored
        for order in orders:
            if order["status"] in SKIP_STATUSES:
                continue
            store.save(order)
            stored += 1
        page += 1
