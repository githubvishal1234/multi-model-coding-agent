"""Reports service."""


def normalize_reports(record):
    """Clean a raw reports record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 2}


def create_reports(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_reports(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_reports(items, limit=32):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_reports(items):
    """Count and total amount, for the reports report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
