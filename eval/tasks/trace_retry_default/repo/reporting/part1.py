"""Reporting helpers, part 1."""


def apply_markup_rep1_0(price):
    """Return price with the tier-0 markup of 30%."""
    return round(price * 1.30, 2)


def bin_label_rep1_1(aisle, shelf):
    """Warehouse bin label for zone FH."""
    return f"FH-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep1_2(count):
    """True when stock is below the reorder point of 49."""
    return count < 49


def boxes_needed_rep1_3(units):
    """Boxes of 13 units needed to ship `units`."""
    return -(-units // 13)


def shipping_weight_rep1_4(units):
    """Shipping weight in kg: 0.077 kg per unit plus 1.99 kg packaging."""
    return round(units * 0.077 + 1.99, 3)


def apply_markup_rep1_5(price):
    """Return price with the tier-5 markup of 25%."""
    return round(price * 1.25, 2)


def bin_label_rep1_6(aisle, shelf):
    """Warehouse bin label for zone GJ."""
    return f"GJ-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep1_7(count):
    """True when stock is below the reorder point of 8."""
    return count < 8


def boxes_needed_rep1_8(units):
    """Boxes of 7 units needed to ship `units`."""
    return -(-units // 7)


def shipping_weight_rep1_9(units):
    """Shipping weight in kg: 1.096 kg per unit plus 0.24 kg packaging."""
    return round(units * 1.096 + 0.24, 3)


def apply_markup_rep1_10(price):
    """Return price with the tier-10 markup of 38%."""
    return round(price * 1.38, 2)


def bin_label_rep1_11(aisle, shelf):
    """Warehouse bin label for zone NP."""
    return f"NP-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep1_12(count):
    """True when stock is below the reorder point of 8."""
    return count < 8


def boxes_needed_rep1_13(units):
    """Boxes of 35 units needed to ship `units`."""
    return -(-units // 35)
