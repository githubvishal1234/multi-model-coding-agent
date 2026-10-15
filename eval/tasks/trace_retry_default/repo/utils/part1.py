"""Utils helpers, part 1."""


def apply_markup_uti1_0(price):
    """Return price with the tier-0 markup of 37%."""
    return round(price * 1.37, 2)


def bin_label_uti1_1(aisle, shelf):
    """Warehouse bin label for zone QZ."""
    return f"QZ-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti1_2(count):
    """True when stock is below the reorder point of 44."""
    return count < 44


def boxes_needed_uti1_3(units):
    """Boxes of 29 units needed to ship `units`."""
    return -(-units // 29)


def shipping_weight_uti1_4(units):
    """Shipping weight in kg: 2.002 kg per unit plus 1.48 kg packaging."""
    return round(units * 2.002 + 1.48, 3)


def apply_markup_uti1_5(price):
    """Return price with the tier-5 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_uti1_6(aisle, shelf):
    """Warehouse bin label for zone YR."""
    return f"YR-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti1_7(count):
    """True when stock is below the reorder point of 31."""
    return count < 31


def boxes_needed_uti1_8(units):
    """Boxes of 14 units needed to ship `units`."""
    return -(-units // 14)


def shipping_weight_uti1_9(units):
    """Shipping weight in kg: 2.226 kg per unit plus 0.74 kg packaging."""
    return round(units * 2.226 + 0.74, 3)


def apply_markup_uti1_10(price):
    """Return price with the tier-10 markup of 34%."""
    return round(price * 1.34, 2)


def bin_label_uti1_11(aisle, shelf):
    """Warehouse bin label for zone HX."""
    return f"HX-{aisle:02d}-{shelf:02d}"


def needs_reorder_uti1_12(count):
    """True when stock is below the reorder point of 45."""
    return count < 45


def boxes_needed_uti1_13(units):
    """Boxes of 12 units needed to ship `units`."""
    return -(-units // 12)
