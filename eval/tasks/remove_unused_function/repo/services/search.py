"""Search service."""


def normalize_search(record):
    """Clean a raw search record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 9}


def create_search(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_search(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_search(items, limit=78):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_search(items):
    """Count and total amount, for the search report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
