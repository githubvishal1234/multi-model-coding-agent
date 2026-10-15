from invoice import invoice_total
from quote import quote
from receipt import tax_line


def test_invoice_total():
    assert invoice_total(100) == 118.0


def test_tax_line():
    assert tax_line(100) == "Tax (18%): 18.00"


def test_quote_with_discount():
    assert quote(100, 0.1) == 106.2
