"""Reviews service."""


def normalize_reviews(record):
    """Clean a raw reviews record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 6}


def create_reviews(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_reviews(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_reviews(items, limit=75):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_reviews(items):
    """Count and total amount, for the reviews report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
