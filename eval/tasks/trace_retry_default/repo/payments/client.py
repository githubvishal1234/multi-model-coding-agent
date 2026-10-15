"""Payment client: charges cards through the bank API."""

from payments.settings import BANK_RETRIES


class BankError(Exception):
    pass


def charge(bank, card, amount):
    """Charge a card, retrying failed bank calls."""
    last_error = None
    for _attempt in range(BANK_RETRIES):
        try:
            return bank.charge(card, amount)
        except BankError as e:
            last_error = e
    raise last_error
