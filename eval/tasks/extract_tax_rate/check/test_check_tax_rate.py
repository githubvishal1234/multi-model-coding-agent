import pathlib

import pytest

import invoice
import quote
import receipt
import settings

MODULES = (invoice, receipt, quote)


def test_constant_defined():
    assert settings.TAX_RATE == 0.18


def test_no_hardcoded_rate_left():
    for mod in MODULES:
        src = pathlib.Path(mod.__file__).read_text()
        for literal in ("0.18", "1.18", "18%"):
            assert literal not in src, f"{literal} still in {mod.__name__}.py"


def test_behaviour_unchanged():
    assert invoice.invoice_total(100) == 118.0
    assert receipt.tax_line(100) == "Tax (18%): 18.00"
    assert quote.quote(100, 0.1) == 106.2


@pytest.fixture
def rate_50(monkeypatch):
    # Patch the constant wherever it lives, whichever import style the fix uses.
    monkeypatch.setattr(settings, "TAX_RATE", 0.5)
    for mod in MODULES:
        if hasattr(mod, "TAX_RATE"):
            monkeypatch.setattr(mod, "TAX_RATE", 0.5)


def test_all_modules_follow_the_constant(rate_50):
    assert invoice.invoice_total(100) == 150.0
    assert receipt.tax_line(100) == "Tax (50%): 50.00"
    assert quote.quote(100, 0.1) == 135.0
