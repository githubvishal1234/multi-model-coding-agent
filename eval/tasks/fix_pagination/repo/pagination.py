def total_pages(count, per_page):
    """Number of pages needed to show `count` items (at least 1)."""
    return max(1, -(-count // per_page))


def paginate(items, page, per_page=10):
    """Return the items shown on a 1-based page."""
    if page < 1 or per_page < 1:
        raise ValueError("page and per_page must be >= 1")
    start = page * per_page
    end = start + per_page
    return items[start:end]
