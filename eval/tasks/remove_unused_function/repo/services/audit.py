"""Audit service."""


def normalize_audit(record):
    """Clean a raw audit record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 9}


def create_audit(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_audit(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_audit(items, limit=86):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_audit(items):
    """Count and total amount, for the audit report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
