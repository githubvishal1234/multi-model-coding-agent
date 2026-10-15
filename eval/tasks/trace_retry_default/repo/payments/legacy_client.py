"""Previous payment client. Kept for reference; nothing imports it."""

RETRIES = 2


def charge_old(bank, card, amount):
    for _ in range(RETRIES):
        try:
            return bank.charge(card, amount)
        except Exception:
            pass
    return None
