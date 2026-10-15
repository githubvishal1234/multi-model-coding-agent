"""Shipping helpers, part 2."""


def apply_markup_shi2_0(price):
    """Return price with the tier-0 markup of 23%."""
    return round(price * 1.23, 2)


def bin_label_shi2_1(aisle, shelf):
    """Warehouse bin label for zone KN."""
    return f"KN-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi2_2(count):
    """True when stock is below the reorder point of 38."""
    return count < 38


def boxes_needed_shi2_3(units):
    """Boxes of 28 units needed to ship `units`."""
    return -(-units // 28)


def shipping_weight_shi2_4(units):
    """Shipping weight in kg: 2.845 kg per unit plus 1.35 kg packaging."""
    return round(units * 2.845 + 1.35, 3)


def apply_markup_shi2_5(price):
    """Return price with the tier-5 markup of 22%."""
    return round(price * 1.22, 2)


def bin_label_shi2_6(aisle, shelf):
    """Warehouse bin label for zone XP."""
    return f"XP-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi2_7(count):
    """True when stock is below the reorder point of 26."""
    return count < 26


def boxes_needed_shi2_8(units):
    """Boxes of 16 units needed to ship `units`."""
    return -(-units // 16)


def shipping_weight_shi2_9(units):
    """Shipping weight in kg: 1.078 kg per unit plus 0.91 kg packaging."""
    return round(units * 1.078 + 0.91, 3)


def apply_markup_shi2_10(price):
    """Return price with the tier-10 markup of 16%."""
    return round(price * 1.16, 2)


def bin_label_shi2_11(aisle, shelf):
    """Warehouse bin label for zone SF."""
    return f"SF-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi2_12(count):
    """True when stock is below the reorder point of 27."""
    return count < 27


def boxes_needed_shi2_13(units):
    """Boxes of 32 units needed to ship `units`."""
    return -(-units // 32)
