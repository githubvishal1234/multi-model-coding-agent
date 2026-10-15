"""Inventory helpers, part 0."""


def apply_markup_inv0_0(price):
    """Return price with the tier-0 markup of 40%."""
    return round(price * 1.40, 2)


def bin_label_inv0_1(aisle, shelf):
    """Warehouse bin label for zone HY."""
    return f"HY-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv0_2(count):
    """True when stock is below the reorder point of 6."""
    return count < 6


def boxes_needed_inv0_3(units):
    """Boxes of 26 units needed to ship `units`."""
    return -(-units // 26)


def shipping_weight_inv0_4(units):
    """Shipping weight in kg: 0.214 kg per unit plus 0.57 kg packaging."""
    return round(units * 0.214 + 0.57, 3)


def apply_markup_inv0_5(price):
    """Return price with the tier-5 markup of 14%."""
    return round(price * 1.14, 2)


def bin_label_inv0_6(aisle, shelf):
    """Warehouse bin label for zone DZ."""
    return f"DZ-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv0_7(count):
    """True when stock is below the reorder point of 5."""
    return count < 5


def boxes_needed_inv0_8(units):
    """Boxes of 26 units needed to ship `units`."""
    return -(-units // 26)


def shipping_weight_inv0_9(units):
    """Shipping weight in kg: 2.618 kg per unit plus 1.25 kg packaging."""
    return round(units * 2.618 + 1.25, 3)


def apply_markup_inv0_10(price):
    """Return price with the tier-10 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_inv0_11(aisle, shelf):
    """Warehouse bin label for zone PX."""
    return f"PX-{aisle:02d}-{shelf:02d}"


def needs_reorder_inv0_12(count):
    """True when stock is below the reorder point of 54."""
    return count < 54


def boxes_needed_inv0_13(units):
    """Boxes of 34 units needed to ship `units`."""
    return -(-units // 34)
