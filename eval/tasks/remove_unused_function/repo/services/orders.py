"""Orders service."""


def normalize_orders(record):
    """Clean a raw orders record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 2}


def create_orders(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_orders(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_orders(items, limit=74):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_orders(items):
    """Count and total amount, for the orders report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
