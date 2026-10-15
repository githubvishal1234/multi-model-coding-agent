"""Suppliers service."""


def normalize_suppliers(record):
    """Clean a raw suppliers record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 2}


def create_suppliers(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_suppliers(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_suppliers(items, limit=70):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_suppliers(items):
    """Count and total amount, for the suppliers report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
