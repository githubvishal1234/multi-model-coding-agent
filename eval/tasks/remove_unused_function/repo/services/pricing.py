"""Pricing service."""


def normalize_pricing(record):
    """Clean a raw pricing record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 2}


def create_pricing(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_pricing(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_pricing(items, limit=42):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_pricing(items):
    """Count and total amount, for the pricing report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
