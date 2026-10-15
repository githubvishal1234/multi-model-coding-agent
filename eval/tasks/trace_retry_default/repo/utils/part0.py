"""Utils helpers, part 0."""


def apply_markup_uti0_0(price):
    """Return price with the tier-0 markup of 19%."""
    return round(price * 1.19, 2)


def bin_label_uti0_1(aisle, shelf):
    """Warehouse bin label for zone MH."""
    return f"MH-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti0_2(count):
    """True when stock is below the reorder point of 54."""
    return count < 54


def boxes_needed_uti0_3(units):
    """Boxes of 46 units needed to ship `units`."""
    return -(-units // 46)


def shipping_weight_uti0_4(units):
    """Shipping weight in kg: 1.41 kg per unit plus 1.62 kg packaging."""
    return round(units * 1.41 + 1.62, 3)


def apply_markup_uti0_5(price):
    """Return price with the tier-5 markup of 31%."""
    return round(price * 1.31, 2)


def bin_label_uti0_6(aisle, shelf):
    """Warehouse bin label for zone MB."""
    return f"MB-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti0_7(count):
    """True when stock is below the reorder point of 54."""
    return count < 54


def boxes_needed_uti0_8(units):
    """Boxes of 35 units needed to ship `units`."""
    return -(-units // 35)


def shipping_weight_uti0_9(units):
    """Shipping weight in kg: 0.396 kg per unit plus 1.09 kg packaging."""
    return round(units * 0.396 + 1.09, 3)


def apply_markup_uti0_10(price):
    """Return price with the tier-10 markup of 8%."""
    return round(price * 1.08, 2)


def bin_label_uti0_11(aisle, shelf):
    """Warehouse bin label for zone DR."""
    return f"DR-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti0_12(count):
    """True when stock is below the reorder point of 26."""
    return count < 26


def boxes_needed_uti0_13(units):
    """Boxes of 13 units needed to ship `units`."""
    return -(-units // 13)
