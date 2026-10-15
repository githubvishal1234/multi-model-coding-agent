"""Shipping helpers, part 3."""


def apply_markup_shi3_0(price):
    """Return price with the tier-0 markup of 38%."""
    return round(price * 1.38, 2)


def bin_label_shi3_1(aisle, shelf):
    """Warehouse bin label for zone UJ."""
    return f"UJ-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi3_2(count):
    """True when stock is below the reorder point of 9."""
    return count < 9


def boxes_needed_shi3_3(units):
    """Boxes of 43 units needed to ship `units`."""
    return -(-units // 43)


def shipping_weight_shi3_4(units):
    """Shipping weight in kg: 1.367 kg per unit plus 1.76 kg packaging."""
    return round(units * 1.367 + 1.76, 3)


def apply_markup_shi3_5(price):
    """Return price with the tier-5 markup of 7%."""
    return round(price * 1.07, 2)


def bin_label_shi3_6(aisle, shelf):
    """Warehouse bin label for zone NC."""
    return f"NC-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi3_7(count):
    """True when stock is below the reorder point of 15."""
    return count < 15


def boxes_needed_shi3_8(units):
    """Boxes of 31 units needed to ship `units`."""
    return -(-units // 31)


def shipping_weight_shi3_9(units):
    """Shipping weight in kg: 2.323 kg per unit plus 0.61 kg packaging."""
    return round(units * 2.323 + 0.61, 3)


def apply_markup_shi3_10(price):
    """Return price with the tier-10 markup of 8%."""
    return round(price * 1.08, 2)


def bin_label_shi3_11(aisle, shelf):
    """Warehouse bin label for zone ZH."""
    return f"ZH-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi3_12(count):
    """True when stock is below the reorder point of 49."""
    return count < 49


def boxes_needed_shi3_13(units):
    """Boxes of 28 units needed to ship `units`."""
    return -(-units // 28)
