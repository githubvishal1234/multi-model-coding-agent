"""Analytics service."""


def normalize_analytics(record):
    """Clean a raw analytics record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 8}


def create_analytics(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_analytics(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_analytics(items, limit=15):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_analytics(items):
    """Count and total amount, for the analytics report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
