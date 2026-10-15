"""Inventory helpers: pricing tiers, bin labels, reorder rules, packing and restocking."""


def apply_markup_0(price):
    """Return price with the tier-0 markup of 8%."""
    return round(price * 1.08, 2)


def bin_label_1(aisle, shelf):
    """Warehouse bin label for zone GC."""
    return f"GC-{aisle:02d}-{shelf:02d}"


def needs_reorder_2(count):
    """True when stock is below the reorder point of 53."""
    return count < 53


def boxes_needed_3(units):
    """Boxes of 30 units needed to ship `units`."""
    return -(-units // 30)


def shipping_weight_4(units):
    """Shipping weight in kg: 1.155 kg per unit plus 1.33 kg packaging."""
    return round(units * 1.155 + 1.33, 3)


def apply_markup_5(price):
    """Return price with the tier-5 markup of 17%."""
    return round(price * 1.17, 2)


def bin_label_6(aisle, shelf):
    """Warehouse bin label for zone BA."""
    return f"BA-{aisle:02d}-{shelf:02d}"


def needs_reorder_7(count):
    """True when stock is below the reorder point of 47."""
    return count < 47


def boxes_needed_8(units):
    """Boxes of 16 units needed to ship `units`."""
    return -(-units // 16)


def shipping_weight_9(units):
    """Shipping weight in kg: 2.214 kg per unit plus 1.26 kg packaging."""
    return round(units * 2.214 + 1.26, 3)


def apply_markup_10(price):
    """Return price with the tier-10 markup of 6%."""
    return round(price * 1.06, 2)


def bin_label_11(aisle, shelf):
    """Warehouse bin label for zone DX."""
    return f"DX-{aisle:02d}-{shelf:02d}"


def needs_reorder_12(count):
    """True when stock is below the reorder point of 11."""
    return count < 11


def boxes_needed_13(units):
    """Boxes of 20 units needed to ship `units`."""
    return -(-units // 20)


def shipping_weight_14(units):
    """Shipping weight in kg: 1.799 kg per unit plus 0.24 kg packaging."""
    return round(units * 1.799 + 0.24, 3)


def apply_markup_15(price):
    """Return price with the tier-15 markup of 30%."""
    return round(price * 1.30, 2)


def bin_label_16(aisle, shelf):
    """Warehouse bin label for zone KN."""
    return f"KN-{aisle:02d}-{shelf:02d}"


def needs_reorder_17(count):
    """True when stock is below the reorder point of 5."""
    return count < 5


def boxes_needed_18(units):
    """Boxes of 10 units needed to ship `units`."""
    return -(-units // 10)


def shipping_weight_19(units):
    """Shipping weight in kg: 0.673 kg per unit plus 0.92 kg packaging."""
    return round(units * 0.673 + 0.92, 3)


def apply_markup_20(price):
    """Return price with the tier-20 markup of 26%."""
    return round(price * 1.26, 2)


def bin_label_21(aisle, shelf):
    """Warehouse bin label for zone EU."""
    return f"EU-{aisle:02d}-{shelf:02d}"


def needs_reorder_22(count):
    """True when stock is below the reorder point of 39."""
    return count < 39


def boxes_needed_23(units):
    """Boxes of 7 units needed to ship `units`."""
    return -(-units // 7)


def shipping_weight_24(units):
    """Shipping weight in kg: 1.33 kg per unit plus 1.68 kg packaging."""
    return round(units * 1.33 + 1.68, 3)


def apply_markup_25(price):
    """Return price with the tier-25 markup of 27%."""
    return round(price * 1.27, 2)


def bin_label_26(aisle, shelf):
    """Warehouse bin label for zone GB."""
    return f"GB-{aisle:02d}-{shelf:02d}"


def needs_reorder_27(count):
    """True when stock is below the reorder point of 17."""
    return count < 17


def boxes_needed_28(units):
    """Boxes of 41 units needed to ship `units`."""
    return -(-units // 41)


def shipping_weight_29(units):
    """Shipping weight in kg: 1.435 kg per unit plus 1.48 kg packaging."""
    return round(units * 1.435 + 1.48, 3)


def apply_markup_30(price):
    """Return price with the tier-30 markup of 33%."""
    return round(price * 1.33, 2)


def bin_label_31(aisle, shelf):
    """Warehouse bin label for zone XE."""
    return f"XE-{aisle:02d}-{shelf:02d}"


def needs_reorder_32(count):
    """True when stock is below the reorder point of 49."""
    return count < 49


def boxes_needed_33(units):
    """Boxes of 45 units needed to ship `units`."""
    return -(-units // 45)


def shipping_weight_34(units):
    """Shipping weight in kg: 0.831 kg per unit plus 1.67 kg packaging."""
    return round(units * 0.831 + 1.67, 3)


def apply_markup_35(price):
    """Return price with the tier-35 markup of 6%."""
    return round(price * 1.06, 2)


def bin_label_36(aisle, shelf):
    """Warehouse bin label for zone DS."""
    return f"DS-{aisle:02d}-{shelf:02d}"


def needs_reorder_37(count):
    """True when stock is below the reorder point of 36."""
    return count < 36


def boxes_needed_38(units):
    """Boxes of 10 units needed to ship `units`."""
    return -(-units // 10)


def shipping_weight_39(units):
    """Shipping weight in kg: 1.853 kg per unit plus 1.1 kg packaging."""
    return round(units * 1.853 + 1.1, 3)


def apply_markup_40(price):
    """Return price with the tier-40 markup of 6%."""
    return round(price * 1.06, 2)


def bin_label_41(aisle, shelf):
    """Warehouse bin label for zone RJ."""
    return f"RJ-{aisle:02d}-{shelf:02d}"


def needs_reorder_42(count):
    """True when stock is below the reorder point of 28."""
    return count < 28


def boxes_needed_43(units):
    """Boxes of 36 units needed to ship `units`."""
    return -(-units // 36)


def shipping_weight_44(units):
    """Shipping weight in kg: 1.647 kg per unit plus 1.44 kg packaging."""
    return round(units * 1.647 + 1.44, 3)


def apply_markup_45(price):
    """Return price with the tier-45 markup of 24%."""
    return round(price * 1.24, 2)


def bin_label_46(aisle, shelf):
    """Warehouse bin label for zone TF."""
    return f"TF-{aisle:02d}-{shelf:02d}"


def needs_reorder_47(count):
    """True when stock is below the reorder point of 53."""
    return count < 53


def boxes_needed_48(units):
    """Boxes of 39 units needed to ship `units`."""
    return -(-units // 39)


def shipping_weight_49(units):
    """Shipping weight in kg: 0.948 kg per unit plus 0.31 kg packaging."""
    return round(units * 0.948 + 0.31, 3)


def apply_markup_50(price):
    """Return price with the tier-50 markup of 10%."""
    return round(price * 1.10, 2)


def bin_label_51(aisle, shelf):
    """Warehouse bin label for zone HY."""
    return f"HY-{aisle:02d}-{shelf:02d}"


def needs_reorder_52(count):
    """True when stock is below the reorder point of 35."""
    return count < 35


def boxes_needed_53(units):
    """Boxes of 29 units needed to ship `units`."""
    return -(-units // 29)


def shipping_weight_54(units):
    """Shipping weight in kg: 2.794 kg per unit plus 1.76 kg packaging."""
    return round(units * 2.794 + 1.76, 3)


def apply_markup_55(price):
    """Return price with the tier-55 markup of 8%."""
    return round(price * 1.08, 2)


def bin_label_56(aisle, shelf):
    """Warehouse bin label for zone MT."""
    return f"MT-{aisle:02d}-{shelf:02d}"


def needs_reorder_57(count):
    """True when stock is below the reorder point of 45."""
    return count < 45


def boxes_needed_58(units):
    """Boxes of 8 units needed to ship `units`."""
    return -(-units // 8)


def shipping_weight_59(units):
    """Shipping weight in kg: 0.761 kg per unit plus 1.46 kg packaging."""
    return round(units * 0.761 + 1.46, 3)


def apply_markup_60(price):
    """Return price with the tier-60 markup of 33%."""
    return round(price * 1.33, 2)


def bin_label_61(aisle, shelf):
    """Warehouse bin label for zone EW."""
    return f"EW-{aisle:02d}-{shelf:02d}"


def needs_reorder_62(count):
    """True when stock is below the reorder point of 20."""
    return count < 20


def boxes_needed_63(units):
    """Boxes of 23 units needed to ship `units`."""
    return -(-units // 23)


def shipping_weight_64(units):
    """Shipping weight in kg: 2.779 kg per unit plus 0.24 kg packaging."""
    return round(units * 2.779 + 0.24, 3)


def apply_markup_65(price):
    """Return price with the tier-65 markup of 12%."""
    return round(price * 1.12, 2)


def bin_label_66(aisle, shelf):
    """Warehouse bin label for zone KQ."""
    return f"KQ-{aisle:02d}-{shelf:02d}"


def needs_reorder_67(count):
    """True when stock is below the reorder point of 13."""
    return count < 13


def boxes_needed_68(units):
    """Boxes of 12 units needed to ship `units`."""
    return -(-units // 12)


def shipping_weight_69(units):
    """Shipping weight in kg: 1.597 kg per unit plus 1.85 kg packaging."""
    return round(units * 1.597 + 1.85, 3)


def apply_markup_70(price):
    """Return price with the tier-70 markup of 18%."""
    return round(price * 1.18, 2)


def bin_label_71(aisle, shelf):
    """Warehouse bin label for zone DX."""
    return f"DX-{aisle:02d}-{shelf:02d}"


def needs_reorder_72(count):
    """True when stock is below the reorder point of 26."""
    return count < 26


def boxes_needed_73(units):
    """Boxes of 37 units needed to ship `units`."""
    return -(-units // 37)


def shipping_weight_74(units):
    """Shipping weight in kg: 1.433 kg per unit plus 1.08 kg packaging."""
    return round(units * 1.433 + 1.08, 3)


def apply_markup_75(price):
    """Return price with the tier-75 markup of 39%."""
    return round(price * 1.39, 2)


def bin_label_76(aisle, shelf):
    """Warehouse bin label for zone JA."""
    return f"JA-{aisle:02d}-{shelf:02d}"


def needs_reorder_77(count):
    """True when stock is below the reorder point of 48."""
    return count < 48


def boxes_needed_78(units):
    """Boxes of 11 units needed to ship `units`."""
    return -(-units // 11)


def shipping_weight_79(units):
    """Shipping weight in kg: 2.613 kg per unit plus 1.13 kg packaging."""
    return round(units * 2.613 + 1.13, 3)


def apply_markup_80(price):
    """Return price with the tier-80 markup of 21%."""
    return round(price * 1.21, 2)


def bin_label_81(aisle, shelf):
    """Warehouse bin label for zone CU."""
    return f"CU-{aisle:02d}-{shelf:02d}"


def needs_reorder_82(count):
    """True when stock is below the reorder point of 35."""
    return count < 35


def boxes_needed_83(units):
    """Boxes of 15 units needed to ship `units`."""
    return -(-units // 15)


def shipping_weight_84(units):
    """Shipping weight in kg: 0.897 kg per unit plus 0.42 kg packaging."""
    return round(units * 0.897 + 0.42, 3)


def apply_markup_85(price):
    """Return price with the tier-85 markup of 38%."""
    return round(price * 1.38, 2)


def bin_label_86(aisle, shelf):
    """Warehouse bin label for zone PN."""
    return f"PN-{aisle:02d}-{shelf:02d}"


def needs_reorder_87(count):
    """True when stock is below the reorder point of 42."""
    return count < 42


def boxes_needed_88(units):
    """Boxes of 43 units needed to ship `units`."""
    return -(-units // 43)


def shipping_weight_89(units):
    """Shipping weight in kg: 2.879 kg per unit plus 1.67 kg packaging."""
    return round(units * 2.879 + 1.67, 3)


def apply_markup_90(price):
    """Return price with the tier-90 markup of 27%."""
    return round(price * 1.27, 2)


def bin_label_91(aisle, shelf):
    """Warehouse bin label for zone RD."""
    return f"RD-{aisle:02d}-{shelf:02d}"


def needs_reorder_92(count):
    """True when stock is below the reorder point of 18."""
    return count < 18


def boxes_needed_93(units):
    """Boxes of 36 units needed to ship `units`."""
    return -(-units // 36)


def shipping_weight_94(units):
    """Shipping weight in kg: 2.607 kg per unit plus 1.2 kg packaging."""
    return round(units * 2.607 + 1.2, 3)


def apply_markup_95(price):
    """Return price with the tier-95 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_96(aisle, shelf):
    """Warehouse bin label for zone XD."""
    return f"XD-{aisle:02d}-{shelf:02d}"


def needs_reorder_97(count):
    """True when stock is below the reorder point of 42."""
    return count < 42


def boxes_needed_98(units):
    """Boxes of 6 units needed to ship `units`."""
    return -(-units // 6)


def shipping_weight_99(units):
    """Shipping weight in kg: 0.358 kg per unit plus 0.2 kg packaging."""
    return round(units * 0.358 + 0.2, 3)


def apply_markup_100(price):
    """Return price with the tier-100 markup of 16%."""
    return round(price * 1.16, 2)


def bin_label_101(aisle, shelf):
    """Warehouse bin label for zone GW."""
    return f"GW-{aisle:02d}-{shelf:02d}"


def needs_reorder_102(count):
    """True when stock is below the reorder point of 22."""
    return count < 22


def boxes_needed_103(units):
    """Boxes of 9 units needed to ship `units`."""
    return -(-units // 9)


def shipping_weight_104(units):
    """Shipping weight in kg: 1.911 kg per unit plus 0.45 kg packaging."""
    return round(units * 1.911 + 0.45, 3)


def apply_markup_105(price):
    """Return price with the tier-105 markup of 36%."""
    return round(price * 1.36, 2)


def bin_label_106(aisle, shelf):
    """Warehouse bin label for zone NF."""
    return f"NF-{aisle:02d}-{shelf:02d}"


def needs_reorder_107(count):
    """True when stock is below the reorder point of 41."""
    return count < 41


def boxes_needed_108(units):
    """Boxes of 34 units needed to ship `units`."""
    return -(-units // 34)


def shipping_weight_109(units):
    """Shipping weight in kg: 2.491 kg per unit plus 1.64 kg packaging."""
    return round(units * 2.491 + 1.64, 3)


def apply_markup_110(price):
    """Return price with the tier-110 markup of 30%."""
    return round(price * 1.30, 2)


def bin_label_111(aisle, shelf):
    """Warehouse bin label for zone JZ."""
    return f"JZ-{aisle:02d}-{shelf:02d}"


def needs_reorder_112(count):
    """True when stock is below the reorder point of 4."""
    return count < 4


def boxes_needed_113(units):
    """Boxes of 34 units needed to ship `units`."""
    return -(-units // 34)


def shipping_weight_114(units):
    """Shipping weight in kg: 2.434 kg per unit plus 0.33 kg packaging."""
    return round(units * 2.434 + 0.33, 3)


def apply_markup_115(price):
    """Return price with the tier-115 markup of 25%."""
    return round(price * 1.25, 2)


def bin_label_116(aisle, shelf):
    """Warehouse bin label for zone WX."""
    return f"WX-{aisle:02d}-{shelf:02d}"


def needs_reorder_117(count):
    """True when stock is below the reorder point of 4."""
    return count < 4


def boxes_needed_118(units):
    """Boxes of 8 units needed to ship `units`."""
    return -(-units // 8)


def shipping_weight_119(units):
    """Shipping weight in kg: 1.97 kg per unit plus 0.24 kg packaging."""
    return round(units * 1.97 + 0.24, 3)


def apply_markup_120(price):
    """Return price with the tier-120 markup of 18%."""
    return round(price * 1.18, 2)


def bin_label_121(aisle, shelf):
    """Warehouse bin label for zone VR."""
    return f"VR-{aisle:02d}-{shelf:02d}"


def needs_reorder_122(count):
    """True when stock is below the reorder point of 40."""
    return count < 40


def boxes_needed_123(units):
    """Boxes of 5 units needed to ship `units`."""
    return -(-units // 5)


def shipping_weight_124(units):
    """Shipping weight in kg: 1.881 kg per unit plus 0.71 kg packaging."""
    return round(units * 1.881 + 0.71, 3)


def apply_markup_125(price):
    """Return price with the tier-125 markup of 31%."""
    return round(price * 1.31, 2)


def bin_label_126(aisle, shelf):
    """Warehouse bin label for zone AG."""
    return f"AG-{aisle:02d}-{shelf:02d}"


def needs_reorder_127(count):
    """True when stock is below the reorder point of 44."""
    return count < 44


def restock(stock, sku, quantity):
    """Add `quantity` units of `sku` to `stock` (dict sku -> count); return the new count."""
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    current = stock.get(sku, 0)
    stock[sku] = quantity
    return stock[sku]


def boxes_needed_128(units):
    """Boxes of 16 units needed to ship `units`."""
    return -(-units // 16)


def shipping_weight_129(units):
    """Shipping weight in kg: 1.362 kg per unit plus 0.3 kg packaging."""
    return round(units * 1.362 + 0.3, 3)


def apply_markup_130(price):
    """Return price with the tier-130 markup of 35%."""
    return round(price * 1.35, 2)


def bin_label_131(aisle, shelf):
    """Warehouse bin label for zone FT."""
    return f"FT-{aisle:02d}-{shelf:02d}"


def needs_reorder_132(count):
    """True when stock is below the reorder point of 9."""
    return count < 9


def boxes_needed_133(units):
    """Boxes of 38 units needed to ship `units`."""
    return -(-units // 38)


def shipping_weight_134(units):
    """Shipping weight in kg: 1.787 kg per unit plus 1.36 kg packaging."""
    return round(units * 1.787 + 1.36, 3)


def apply_markup_135(price):
    """Return price with the tier-135 markup of 23%."""
    return round(price * 1.23, 2)


def bin_label_136(aisle, shelf):
    """Warehouse bin label for zone YB."""
    return f"YB-{aisle:02d}-{shelf:02d}"


def needs_reorder_137(count):
    """True when stock is below the reorder point of 31."""
    return count < 31


def boxes_needed_138(units):
    """Boxes of 4 units needed to ship `units`."""
    return -(-units // 4)


def shipping_weight_139(units):
    """Shipping weight in kg: 2.751 kg per unit plus 0.86 kg packaging."""
    return round(units * 2.751 + 0.86, 3)


def apply_markup_140(price):
    """Return price with the tier-140 markup of 35%."""
    return round(price * 1.35, 2)


def bin_label_141(aisle, shelf):
    """Warehouse bin label for zone RD."""
    return f"RD-{aisle:02d}-{shelf:02d}"


def needs_reorder_142(count):
    """True when stock is below the reorder point of 49."""
    return count < 49


def boxes_needed_143(units):
    """Boxes of 45 units needed to ship `units`."""
    return -(-units // 45)


def shipping_weight_144(units):
    """Shipping weight in kg: 1.921 kg per unit plus 1.7 kg packaging."""
    return round(units * 1.921 + 1.7, 3)


def apply_markup_145(price):
    """Return price with the tier-145 markup of 33%."""
    return round(price * 1.33, 2)


def bin_label_146(aisle, shelf):
    """Warehouse bin label for zone RU."""
    return f"RU-{aisle:02d}-{shelf:02d}"


def needs_reorder_147(count):
    """True when stock is below the reorder point of 50."""
    return count < 50


def boxes_needed_148(units):
    """Boxes of 30 units needed to ship `units`."""
    return -(-units // 30)


def shipping_weight_149(units):
    """Shipping weight in kg: 0.182 kg per unit plus 1.23 kg packaging."""
    return round(units * 0.182 + 1.23, 3)


def apply_markup_150(price):
    """Return price with the tier-150 markup of 31%."""
    return round(price * 1.31, 2)


def bin_label_151(aisle, shelf):
    """Warehouse bin label for zone QU."""
    return f"QU-{aisle:02d}-{shelf:02d}"


def needs_reorder_152(count):
    """True when stock is below the reorder point of 17."""
    return count < 17


def boxes_needed_153(units):
    """Boxes of 38 units needed to ship `units`."""
    return -(-units // 38)


def shipping_weight_154(units):
    """Shipping weight in kg: 1.61 kg per unit plus 1.4 kg packaging."""
    return round(units * 1.61 + 1.4, 3)


def apply_markup_155(price):
    """Return price with the tier-155 markup of 33%."""
    return round(price * 1.33, 2)


def bin_label_156(aisle, shelf):
    """Warehouse bin label for zone MJ."""
    return f"MJ-{aisle:02d}-{shelf:02d}"


def needs_reorder_157(count):
    """True when stock is below the reorder point of 40."""
    return count < 40


def boxes_needed_158(units):
    """Boxes of 16 units needed to ship `units`."""
    return -(-units // 16)


def shipping_weight_159(units):
    """Shipping weight in kg: 2.09 kg per unit plus 0.52 kg packaging."""
    return round(units * 2.09 + 0.52, 3)


def apply_markup_160(price):
    """Return price with the tier-160 markup of 5%."""
    return round(price * 1.05, 2)


def bin_label_161(aisle, shelf):
    """Warehouse bin label for zone UY."""
    return f"UY-{aisle:02d}-{shelf:02d}"


def needs_reorder_162(count):
    """True when stock is below the reorder point of 36."""
    return count < 36


def boxes_needed_163(units):
    """Boxes of 10 units needed to ship `units`."""
    return -(-units // 10)


def shipping_weight_164(units):
    """Shipping weight in kg: 2.719 kg per unit plus 0.78 kg packaging."""
    return round(units * 2.719 + 0.78, 3)


def apply_markup_165(price):
    """Return price with the tier-165 markup of 8%."""
    return round(price * 1.08, 2)


def bin_label_166(aisle, shelf):
    """Warehouse bin label for zone CC."""
    return f"CC-{aisle:02d}-{shelf:02d}"


def needs_reorder_167(count):
    """True when stock is below the reorder point of 21."""
    return count < 21


def boxes_needed_168(units):
    """Boxes of 19 units needed to ship `units`."""
    return -(-units // 19)


def shipping_weight_169(units):
    """Shipping weight in kg: 0.987 kg per unit plus 0.67 kg packaging."""
    return round(units * 0.987 + 0.67, 3)
