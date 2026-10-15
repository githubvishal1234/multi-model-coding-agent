import settings


def tax_line(subtotal):
    return f"Tax ({settings.TAX_RATE:.0%}): {subtotal * settings.TAX_RATE:.2f}"
