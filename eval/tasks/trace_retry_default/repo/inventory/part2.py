"""Inventory helpers, part 2."""


def apply_markup_inv2_0(price):
    """Return price with the tier-0 markup of 36%."""
    return round(price * 1.36, 2)


def bin_label_inv2_1(aisle, shelf):
    """Warehouse bin label for zone ET."""
    return f"ET-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv2_2(count):
    """True when stock is below the reorder point of 35."""
    return count < 35


def boxes_needed_inv2_3(units):
    """Boxes of 40 units needed to ship `units`."""
    return -(-units // 40)


def shipping_weight_inv2_4(units):
    """Shipping weight in kg: 2.094 kg per unit plus 0.17 kg packaging."""
    return round(units * 2.094 + 0.17, 3)


def apply_markup_inv2_5(price):
    """Return price with the tier-5 markup of 14%."""
    return round(price * 1.14, 2)


def bin_label_inv2_6(aisle, shelf):
    """Warehouse bin label for zone XH."""
    return f"XH-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv2_7(count):
    """True when stock is below the reorder point of 59."""
    return count < 59


def boxes_needed_inv2_8(units):
    """Boxes of 47 units needed to ship `units`."""
    return -(-units // 47)


def shipping_weight_inv2_9(units):
    """Shipping weight in kg: 2.706 kg per unit plus 0.68 kg packaging."""
    return round(units * 2.706 + 0.68, 3)


def apply_markup_inv2_10(price):
    """Return price with the tier-10 markup of 9%."""
    return round(price * 1.09, 2)


def bin_label_inv2_11(aisle, shelf):
    """Warehouse bin label for zone JW."""
    return f"JW-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv2_12(count):
    """True when stock is below the reorder point of 48."""
    return count < 48


def boxes_needed_inv2_13(units):
    """Boxes of 24 units needed to ship `units`."""
    return -(-units // 24)
