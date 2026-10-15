"""Exports service."""


def normalize_exports(record):
    """Clean a raw exports record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 2}


def create_exports(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_exports(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_exports(items, limit=84):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_exports(items):
    """Count and total amount, for the exports report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
