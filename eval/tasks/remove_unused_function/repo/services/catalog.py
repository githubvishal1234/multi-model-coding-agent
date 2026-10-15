"""Catalog service."""


def normalize_catalog(record):
    """Clean a raw catalog record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 2}


def create_catalog(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_catalog(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_catalog(items, limit=24):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_catalog(items):
    """Count and total amount, for the catalog report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
