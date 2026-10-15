import settings


def quote(subtotal, discount=0.0):
    taxed = subtotal * (1 + settings.TAX_RATE)
    return round(taxed * (1 - discount), 2)
