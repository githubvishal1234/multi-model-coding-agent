"""Reporting helpers, part 0."""


def apply_markup_rep0_0(price):
    """Return price with the tier-0 markup of 30%."""
    return round(price * 1.30, 2)


def bin_label_rep0_1(aisle, shelf):
    """Warehouse bin label for zone EK."""
    return f"EK-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep0_2(count):
    """True when stock is below the reorder point of 6."""
    return count < 6


def boxes_needed_rep0_3(units):
    """Boxes of 34 units needed to ship `units`."""
    return -(-units // 34)


def shipping_weight_rep0_4(units):
    """Shipping weight in kg: 1.867 kg per unit plus 0.53 kg packaging."""
    return round(units * 1.867 + 0.53, 3)


def apply_markup_rep0_5(price):
    """Return price with the tier-5 markup of 35%."""
    return round(price * 1.35, 2)


def bin_label_rep0_6(aisle, shelf):
    """Warehouse bin label for zone MV."""
    return f"MV-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep0_7(count):
    """True when stock is below the reorder point of 5."""
    return count < 5


def boxes_needed_rep0_8(units):
    """Boxes of 31 units needed to ship `units`."""
    return -(-units // 31)


def shipping_weight_rep0_9(units):
    """Shipping weight in kg: 2.744 kg per unit plus 0.8 kg packaging."""
    return round(units * 2.744 + 0.8, 3)


def apply_markup_rep0_10(price):
    """Return price with the tier-10 markup of 11%."""
    return round(price * 1.11, 2)


def bin_label_rep0_11(aisle, shelf):
    """Warehouse bin label for zone NQ."""
    return f"NQ-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep0_12(count):
    """True when stock is below the reorder point of 52."""
    return count < 52


def boxes_needed_rep0_13(units):
    """Boxes of 34 units needed to ship `units`."""
    return -(-units // 34)
