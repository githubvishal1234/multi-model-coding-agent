"""Shipping service."""


def normalize_shipping(record):
    """Clean a raw shipping record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 3}


def create_shipping(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_shipping(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_shipping(items, limit=42):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_shipping(items):
    """Count and total amount, for the shipping report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
