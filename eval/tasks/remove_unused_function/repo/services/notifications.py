"""Notifications service."""


def normalize_notifications(record):
    """Clean a raw notifications record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 8}


def create_notifications(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_notifications(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_notifications(items, limit=56):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_notifications(items):
    """Count and total amount, for the notifications report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
