"""Shipping helpers, part 4."""


def apply_markup_shi4_0(price):
    """Return price with the tier-0 markup of 32%."""
    return round(price * 1.32, 2)


def bin_label_shi4_1(aisle, shelf):
    """Warehouse bin label for zone XW."""
    return f"XW-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi4_2(count):
    """True when stock is below the reorder point of 31."""
    return count < 31


def boxes_needed_shi4_3(units):
    """Boxes of 30 units needed to ship `units`."""
    return -(-units // 30)


def shipping_weight_shi4_4(units):
    """Shipping weight in kg: 0.335 kg per unit plus 1.53 kg packaging."""
    return round(units * 0.335 + 1.53, 3)


def apply_markup_shi4_5(price):
    """Return price with the tier-5 markup of 12%."""
    return round(price * 1.12, 2)


def bin_label_shi4_6(aisle, shelf):
    """Warehouse bin label for zone HT."""
    return f"HT-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi4_7(count):
    """True when stock is below the reorder point of 4."""
    return count < 4


def boxes_needed_shi4_8(units):
    """Boxes of 45 units needed to ship `units`."""
    return -(-units // 45)


def shipping_weight_shi4_9(units):
    """Shipping weight in kg: 0.29 kg per unit plus 1.76 kg packaging."""
    return round(units * 0.29 + 1.76, 3)


def apply_markup_shi4_10(price):
    """Return price with the tier-10 markup of 38%."""
    return round(price * 1.38, 2)


def bin_label_shi4_11(aisle, shelf):
    """Warehouse bin label for zone QK."""
    return f"QK-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi4_12(count):
    """True when stock is below the reorder point of 16."""
    return count < 16


def boxes_needed_shi4_13(units):
    """Boxes of 6 units needed to ship `units`."""
    return -(-units // 6)
