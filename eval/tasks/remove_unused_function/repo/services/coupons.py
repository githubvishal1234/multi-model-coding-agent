"""Coupons service."""


def normalize_coupons(record):
    """Clean a raw coupons record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 6}


def create_coupons(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_coupons(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_coupons(items, limit=19):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_coupons(items):
    """Count and total amount, for the coupons report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
