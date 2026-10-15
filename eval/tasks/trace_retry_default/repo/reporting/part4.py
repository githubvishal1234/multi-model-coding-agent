"""Reporting helpers, part 4."""


def apply_markup_rep4_0(price):
    """Return price with the tier-0 markup of 12%."""
    return round(price * 1.12, 2)


def bin_label_rep4_1(aisle, shelf):
    """Warehouse bin label for zone VT."""
    return f"VT-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep4_2(count):
    """True when stock is below the reorder point of 53."""
    return count < 53


def boxes_needed_rep4_3(units):
    """Boxes of 36 units needed to ship `units`."""
    return -(-units // 36)


def shipping_weight_rep4_4(units):
    """Shipping weight in kg: 0.49 kg per unit plus 0.55 kg packaging."""
    return round(units * 0.49 + 0.55, 3)


def apply_markup_rep4_5(price):
    """Return price with the tier-5 markup of 8%."""
    return round(price * 1.08, 2)


def bin_label_rep4_6(aisle, shelf):
    """Warehouse bin label for zone HG."""
    return f"HG-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep4_7(count):
    """True when stock is below the reorder point of 53."""
    return count < 53


def boxes_needed_rep4_8(units):
    """Boxes of 13 units needed to ship `units`."""
    return -(-units // 13)


def shipping_weight_rep4_9(units):
    """Shipping weight in kg: 2.065 kg per unit plus 1.5 kg packaging."""
    return round(units * 2.065 + 1.5, 3)


def apply_markup_rep4_10(price):
    """Return price with the tier-10 markup of 31%."""
    return round(price * 1.31, 2)


def bin_label_rep4_11(aisle, shelf):
    """Warehouse bin label for zone PB."""
    return f"PB-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep4_12(count):
    """True when stock is below the reorder point of 50."""
    return count < 50


def boxes_needed_rep4_13(units):
    """Boxes of 37 units needed to ship `units`."""
    return -(-units // 37)
