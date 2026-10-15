"""Billing service."""


def normalize_billing(record):
    """Clean a raw billing record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 7}


def create_billing(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_billing(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_billing(items, limit=92):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_billing(items):
    """Count and total amount, for the billing report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
