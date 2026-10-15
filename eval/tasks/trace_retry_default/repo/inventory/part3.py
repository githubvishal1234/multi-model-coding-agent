"""Inventory helpers, part 3."""


def apply_markup_inv3_0(price):
    """Return price with the tier-0 markup of 21%."""
    return round(price * 1.21, 2)


def bin_label_inv3_1(aisle, shelf):
    """Warehouse bin label for zone HD."""
    return f"HD-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv3_2(count):
    """True when stock is below the reorder point of 56."""
    return count < 56


def boxes_needed_inv3_3(units):
    """Boxes of 19 units needed to ship `units`."""
    return -(-units // 19)


def shipping_weight_inv3_4(units):
    """Shipping weight in kg: 2.345 kg per unit plus 1.68 kg packaging."""
    return round(units * 2.345 + 1.68, 3)


def apply_markup_inv3_5(price):
    """Return price with the tier-5 markup of 12%."""
    return round(price * 1.12, 2)


def bin_label_inv3_6(aisle, shelf):
    """Warehouse bin label for zone PR."""
    return f"PR-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv3_7(count):
    """True when stock is below the reorder point of 50."""
    return count < 50


def boxes_needed_inv3_8(units):
    """Boxes of 9 units needed to ship `units`."""
    return -(-units // 9)


def shipping_weight_inv3_9(units):
    """Shipping weight in kg: 0.148 kg per unit plus 0.61 kg packaging."""
    return round(units * 0.148 + 0.61, 3)


def apply_markup_inv3_10(price):
    """Return price with the tier-10 markup of 33%."""
    return round(price * 1.33, 2)


def bin_label_inv3_11(aisle, shelf):
    """Warehouse bin label for zone MQ."""
    return f"MQ-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv3_12(count):
    """True when stock is below the reorder point of 57."""
    return count < 57


def boxes_needed_inv3_13(units):
    """Boxes of 29 units needed to ship `units`."""
    return -(-units // 29)
