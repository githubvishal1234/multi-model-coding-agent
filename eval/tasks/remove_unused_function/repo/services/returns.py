"""Returns service."""


def normalize_returns(record):
    """Clean a raw returns record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 2}


def create_returns(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_returns(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_returns(items, limit=53):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_returns(items):
    """Count and total amount, for the returns report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
