"""Inventory helpers, part 4."""


def apply_markup_inv4_0(price):
    """Return price with the tier-0 markup of 22%."""
    return round(price * 1.22, 2)


def bin_label_inv4_1(aisle, shelf):
    """Warehouse bin label for zone ZB."""
    return f"ZB-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv4_2(count):
    """True when stock is below the reorder point of 17."""
    return count < 17


def boxes_needed_inv4_3(units):
    """Boxes of 13 units needed to ship `units`."""
    return -(-units // 13)


def shipping_weight_inv4_4(units):
    """Shipping weight in kg: 0.13 kg per unit plus 1.0 kg packaging."""
    return round(units * 0.13 + 1.0, 3)


def apply_markup_inv4_5(price):
    """Return price with the tier-5 markup of 9%."""
    return round(price * 1.09, 2)


def bin_label_inv4_6(aisle, shelf):
    """Warehouse bin label for zone DJ."""
    return f"DJ-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv4_7(count):
    """True when stock is below the reorder point of 24."""
    return count < 24


def boxes_needed_inv4_8(units):
    """Boxes of 38 units needed to ship `units`."""
    return -(-units // 38)


def shipping_weight_inv4_9(units):
    """Shipping weight in kg: 1.527 kg per unit plus 1.03 kg packaging."""
    return round(units * 1.527 + 1.03, 3)


def apply_markup_inv4_10(price):
    """Return price with the tier-10 markup of 13%."""
    return round(price * 1.13, 2)


def bin_label_inv4_11(aisle, shelf):
    """Warehouse bin label for zone KT."""
    return f"KT-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv4_12(count):
    """True when stock is below the reorder point of 24."""
    return count < 24


def boxes_needed_inv4_13(units):
    """Boxes of 26 units needed to ship `units`."""
    return -(-units // 26)
