"""Utils helpers, part 4."""


def apply_markup_uti4_0(price):
    """Return price with the tier-0 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_uti4_1(aisle, shelf):
    """Warehouse bin label for zone PZ."""
    return f"PZ-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti4_2(count):
    """True when stock is below the reorder point of 45."""
    return count < 45


def boxes_needed_uti4_3(units):
    """Boxes of 37 units needed to ship `units`."""
    return -(-units // 37)


def shipping_weight_uti4_4(units):
    """Shipping weight in kg: 1.83 kg per unit plus 1.56 kg packaging."""
    return round(units * 1.83 + 1.56, 3)


def apply_markup_uti4_5(price):
    """Return price with the tier-5 markup of 22%."""
    return round(price * 1.22, 2)


def bin_label_uti4_6(aisle, shelf):
    """Warehouse bin label for zone GD."""
    return f"GD-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti4_7(count):
    """True when stock is below the reorder point of 23."""
    return count < 23


def boxes_needed_uti4_8(units):
    """Boxes of 16 units needed to ship `units`."""
    return -(-units // 16)


def shipping_weight_uti4_9(units):
    """Shipping weight in kg: 2.262 kg per unit plus 1.86 kg packaging."""
    return round(units * 2.262 + 1.86, 3)


def apply_markup_uti4_10(price):
    """Return price with the tier-10 markup of 27%."""
    return round(price * 1.27, 2)


def bin_label_uti4_11(aisle, shelf):
    """Warehouse bin label for zone YP."""
    return f"YP-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti4_12(count):
    """True when stock is below the reorder point of 52."""
    return count < 52


def boxes_needed_uti4_13(units):
    """Boxes of 35 units needed to ship `units`."""
    return -(-units // 35)
