import settings


def invoice_total(subtotal):
    return round(subtotal * (1 + settings.TAX_RATE), 2)
