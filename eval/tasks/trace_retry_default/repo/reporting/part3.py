"""Reporting helpers, part 3."""


def apply_markup_rep3_0(price):
    """Return price with the tier-0 markup of 27%."""
    return round(price * 1.27, 2)


def bin_label_rep3_1(aisle, shelf):
    """Warehouse bin label for zone HY."""
    return f"HY-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep3_2(count):
    """True when stock is below the reorder point of 54."""
    return count < 54


def boxes_needed_rep3_3(units):
    """Boxes of 23 units needed to ship `units`."""
    return -(-units // 23)


def shipping_weight_rep3_4(units):
    """Shipping weight in kg: 1.919 kg per unit plus 0.51 kg packaging."""
    return round(units * 1.919 + 0.51, 3)


def apply_markup_rep3_5(price):
    """Return price with the tier-5 markup of 15%."""
    return round(price * 1.15, 2)


def bin_label_rep3_6(aisle, shelf):
    """Warehouse bin label for zone TQ."""
    return f"TQ-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep3_7(count):
    """True when stock is below the reorder point of 49."""
    return count < 49


def boxes_needed_rep3_8(units):
    """Boxes of 47 units needed to ship `units`."""
    return -(-units // 47)


def shipping_weight_rep3_9(units):
    """Shipping weight in kg: 0.193 kg per unit plus 1.51 kg packaging."""
    return round(units * 0.193 + 1.51, 3)


def apply_markup_rep3_10(price):
    """Return price with the tier-10 markup of 32%."""
    return round(price * 1.32, 2)


def bin_label_rep3_11(aisle, shelf):
    """Warehouse bin label for zone QD."""
    return f"QD-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep3_12(count):
    """True when stock is below the reorder point of 56."""
    return count < 56


def boxes_needed_rep3_13(units):
    """Boxes of 8 units needed to ship `units`."""
    return -(-units // 8)
