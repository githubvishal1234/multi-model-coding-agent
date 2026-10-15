"""Reporting helpers, part 2."""


def apply_markup_rep2_0(price):
    """Return price with the tier-0 markup of 7%."""
    return round(price * 1.07, 2)


def bin_label_rep2_1(aisle, shelf):
    """Warehouse bin label for zone GY."""
    return f"GY-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep2_2(count):
    """True when stock is below the reorder point of 20."""
    return count < 20


def boxes_needed_rep2_3(units):
    """Boxes of 44 units needed to ship `units`."""
    return -(-units // 44)


def shipping_weight_rep2_4(units):
    """Shipping weight in kg: 2.074 kg per unit plus 0.99 kg packaging."""
    return round(units * 2.074 + 0.99, 3)


def apply_markup_rep2_5(price):
    """Return price with the tier-5 markup of 28%."""
    return round(price * 1.28, 2)


def bin_label_rep2_6(aisle, shelf):
    """Warehouse bin label for zone DE."""
    return f"DE-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep2_7(count):
    """True when stock is below the reorder point of 22."""
    return count < 22


def boxes_needed_rep2_8(units):
    """Boxes of 38 units needed to ship `units`."""
    return -(-units // 38)


def shipping_weight_rep2_9(units):
    """Shipping weight in kg: 2.538 kg per unit plus 0.81 kg packaging."""
    return round(units * 2.538 + 0.81, 3)


def apply_markup_rep2_10(price):
    """Return price with the tier-10 markup of 18%."""
    return round(price * 1.18, 2)


def bin_label_rep2_11(aisle, shelf):
    """Warehouse bin label for zone WG."""
    return f"WG-{aisle:02d}-{shelf:02d}"


def needs_reorder_rep2_12(count):
    """True when stock is below the reorder point of 28."""
    return count < 28


def boxes_needed_rep2_13(units):
    """Boxes of 33 units needed to ship `units`."""
    return -(-units // 33)
