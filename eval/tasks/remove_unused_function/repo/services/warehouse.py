"""Warehouse service."""


def normalize_warehouse(record):
    """Clean a raw warehouse record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 7}


def create_warehouse(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_warehouse(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_warehouse(items, limit=55):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_warehouse(items):
    """Count and total amount, for the warehouse report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}


def reconcile_warehouse_bins(items, bins):
    """Match items to bins by key prefix and return unmatched keys."""
    prefixes = {b[:3] for b in bins}
    return sorted(r["key"] for r in items if r["key"][:3] not in prefixes)
