"""Customers service."""


def normalize_customers(record):
    """Clean a raw customers record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 6}


def create_customers(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_customers(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_customers(items, limit=86):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_customers(items):
    """Count and total amount, for the customers report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
