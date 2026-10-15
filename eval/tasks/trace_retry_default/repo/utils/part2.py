"""Utils helpers, part 2."""


def apply_markup_uti2_0(price):
    """Return price with the tier-0 markup of 8%."""
    return round(price * 1.08, 2)


def bin_label_uti2_1(aisle, shelf):
    """Warehouse bin label for zone RS."""
    return f"RS-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti2_2(count):
    """True when stock is below the reorder point of 26."""
    return count < 26


def boxes_needed_uti2_3(units):
    """Boxes of 7 units needed to ship `units`."""
    return -(-units // 7)


def shipping_weight_uti2_4(units):
    """Shipping weight in kg: 1.497 kg per unit plus 0.31 kg packaging."""
    return round(units * 1.497 + 0.31, 3)


def apply_markup_uti2_5(price):
    """Return price with the tier-5 markup of 10%."""
    return round(price * 1.10, 2)


def bin_label_uti2_6(aisle, shelf):
    """Warehouse bin label for zone WK."""
    return f"WK-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti2_7(count):
    """True when stock is below the reorder point of 25."""
    return count < 25


def boxes_needed_uti2_8(units):
    """Boxes of 31 units needed to ship `units`."""
    return -(-units // 31)


def shipping_weight_uti2_9(units):
    """Shipping weight in kg: 0.573 kg per unit plus 1.57 kg packaging."""
    return round(units * 0.573 + 1.57, 3)


def apply_markup_uti2_10(price):
    """Return price with the tier-10 markup of 30%."""
    return round(price * 1.30, 2)


def bin_label_uti2_11(aisle, shelf):
    """Warehouse bin label for zone CX."""
    return f"CX-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti2_12(count):
    """True when stock is below the reorder point of 36."""
    return count < 36


def boxes_needed_uti2_13(units):
    """Boxes of 8 units needed to ship `units`."""
    return -(-units // 8)
