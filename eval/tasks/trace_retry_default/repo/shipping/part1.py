"""Shipping helpers, part 1."""


def apply_markup_shi1_0(price):
    """Return price with the tier-0 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_shi1_1(aisle, shelf):
    """Warehouse bin label for zone GR."""
    return f"GR-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi1_2(count):
    """True when stock is below the reorder point of 16."""
    return count < 16


def boxes_needed_shi1_3(units):
    """Boxes of 44 units needed to ship `units`."""
    return -(-units // 44)


def shipping_weight_shi1_4(units):
    """Shipping weight in kg: 2.366 kg per unit plus 1.41 kg packaging."""
    return round(units * 2.366 + 1.41, 3)


def apply_markup_shi1_5(price):
    """Return price with the tier-5 markup of 15%."""
    return round(price * 1.15, 2)


def bin_label_shi1_6(aisle, shelf):
    """Warehouse bin label for zone HX."""
    return f"HX-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi1_7(count):
    """True when stock is below the reorder point of 50."""
    return count < 50


def boxes_needed_shi1_8(units):
    """Boxes of 37 units needed to ship `units`."""
    return -(-units // 37)


def shipping_weight_shi1_9(units):
    """Shipping weight in kg: 0.223 kg per unit plus 1.39 kg packaging."""
    return round(units * 0.223 + 1.39, 3)


def apply_markup_shi1_10(price):
    """Return price with the tier-10 markup of 39%."""
    return round(price * 1.39, 2)


def bin_label_shi1_11(aisle, shelf):
    """Warehouse bin label for zone HM."""
    return f"HM-{aisle:02d}-{shelf:02d}"


def needs_reorder_shi1_12(count):
    """True when stock is below the reorder point of 7."""
    return count < 7


def boxes_needed_shi1_13(units):
    """Boxes of 40 units needed to ship `units`."""
    return -(-units // 40)
