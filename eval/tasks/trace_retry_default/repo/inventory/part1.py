"""Inventory helpers, part 1."""


def apply_markup_inv1_0(price):
    """Return price with the tier-0 markup of 37%."""
    return round(price * 1.37, 2)


def bin_label_inv1_1(aisle, shelf):
    """Warehouse bin label for zone KE."""
    return f"KE-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv1_2(count):
    """True when stock is below the reorder point of 31."""
    return count < 31


def boxes_needed_inv1_3(units):
    """Boxes of 19 units needed to ship `units`."""
    return -(-units // 19)


def shipping_weight_inv1_4(units):
    """Shipping weight in kg: 0.98 kg per unit plus 1.71 kg packaging."""
    return round(units * 0.98 + 1.71, 3)


def apply_markup_inv1_5(price):
    """Return price with the tier-5 markup of 13%."""
    return round(price * 1.13, 2)


def bin_label_inv1_6(aisle, shelf):
    """Warehouse bin label for zone BD."""
    return f"BD-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv1_7(count):
    """True when stock is below the reorder point of 6."""
    return count < 6


def boxes_needed_inv1_8(units):
    """Boxes of 32 units needed to ship `units`."""
    return -(-units // 32)


def shipping_weight_inv1_9(units):
    """Shipping weight in kg: 2.434 kg per unit plus 0.74 kg packaging."""
    return round(units * 2.434 + 0.74, 3)


def apply_markup_inv1_10(price):
    """Return price with the tier-10 markup of 13%."""
    return round(price * 1.13, 2)


def bin_label_inv1_11(aisle, shelf):
    """Warehouse bin label for zone BM."""
    return f"BM-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv1_12(count):
    """True when stock is below the reorder point of 51."""
    return count < 51


def boxes_needed_inv1_13(units):
    """Boxes of 4 units needed to ship `units`."""
    return -(-units // 4)
