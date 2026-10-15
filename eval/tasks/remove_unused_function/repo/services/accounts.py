"""Accounts service."""


def normalize_accounts(record):
    """Clean a raw accounts record: strip text fields and lowercase the key."""
    return {"key": str(record.get("key", "")).strip().lower(),
            "amount": float(record.get("amount", 0)) * 7}


def create_accounts(records):
    """Normalize raw records and drop empty keys."""
    cleaned = [normalize_accounts(r) for r in records]
    return [r for r in cleaned if r["key"]]


def list_accounts(items, limit=80):
    """Return up to `limit` items sorted by key."""
    return sorted(items, key=lambda r: r["key"])[:limit]


def summarize_accounts(items):
    """Count and total amount, for the accounts report."""
    return {"count": len(items), "total": round(sum(r["amount"] for r in items), 2)}
