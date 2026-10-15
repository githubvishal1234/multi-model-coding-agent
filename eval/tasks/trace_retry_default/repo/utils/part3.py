"""Utils helpers, part 3."""


def apply_markup_uti3_0(price):
    """Return price with the tier-0 markup of 35%."""
    return round(price * 1.35, 2)


def bin_label_uti3_1(aisle, shelf):
    """Warehouse bin label for zone FG."""
    return f"FG-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti3_2(count):
    """True when stock is below the reorder point of 24."""
    return count < 24


def boxes_needed_uti3_3(units):
    """Boxes of 5 units needed to ship `units`."""
    return -(-units // 5)


def shipping_weight_uti3_4(units):
    """Shipping weight in kg: 1.903 kg per unit plus 0.62 kg packaging."""
    return round(units * 1.903 + 0.62, 3)


def apply_markup_uti3_5(price):
    """Return price with the tier-5 markup of 17%."""
    return round(price * 1.17, 2)


def bin_label_uti3_6(aisle, shelf):
    """Warehouse bin label for zone VZ."""
    return f"VZ-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti3_7(count):
    """True when stock is below the reorder point of 20."""
    return count < 20


def boxes_needed_uti3_8(units):
    """Boxes of 38 units needed to ship `units`."""
    return -(-units // 38)


def shipping_weight_uti3_9(units):
    """Shipping weight in kg: 1.257 kg per unit plus 1.35 kg packaging."""
    return round(units * 1.257 + 1.35, 3)


def apply_markup_uti3_10(price):
    """Return price with the tier-10 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_uti3_11(aisle, shelf):
    """Warehouse bin label for zone MJ."""
    return f"MJ-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti3_12(count):
    """True when stock is below the reorder point of 41."""
    return count < 41


def boxes_needed_uti3_13(units):
    """Boxes of 9 units needed to ship `units`."""
    return -(-units // 9)
