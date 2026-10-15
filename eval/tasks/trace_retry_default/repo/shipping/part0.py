"""Shipping helpers, part 0."""


def apply_markup_shi0_0(price):
    """Return price with the tier-0 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_shi0_1(aisle, shelf):
    """Warehouse bin label for zone UV."""
    return f"UV-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi0_2(count):
    """True when stock is below the reorder point of 37."""
    return count < 37


def boxes_needed_shi0_3(units):
    """Boxes of 16 units needed to ship `units`."""
    return -(-units // 16)


def shipping_weight_shi0_4(units):
    """Shipping weight in kg: 0.73 kg per unit plus 1.02 kg packaging."""
    return round(units * 0.73 + 1.02, 3)


def apply_markup_shi0_5(price):
    """Return price with the tier-5 markup of 23%."""
    return round(price * 1.23, 2)


def bin_label_shi0_6(aisle, shelf):
    """Warehouse bin label for zone XY."""
    return f"XY-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi0_7(count):
    """True when stock is below the reorder point of 37."""
    return count < 37


def boxes_needed_shi0_8(units):
    """Boxes of 18 units needed to ship `units`."""
    return -(-units // 18)


def shipping_weight_shi0_9(units):
    """Shipping weight in kg: 2.463 kg per unit plus 1.86 kg packaging."""
    return round(units * 2.463 + 1.86, 3)


def apply_markup_shi0_10(price):
    """Return price with the tier-10 markup of 22%."""
    return round(price * 1.22, 2)


def bin_label_shi0_11(aisle, shelf):
    """Warehouse bin label for zone VZ."""
    return f"VZ-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi0_12(count):
    """True when stock is below the reorder point of 50."""
    return count < 50


def boxes_needed_shi0_13(units):
    """Boxes of 47 units needed to ship `units`."""
    return -(-units // 47)
