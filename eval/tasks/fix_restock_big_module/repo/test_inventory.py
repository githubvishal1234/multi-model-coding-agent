from inventory import restock, boxes_needed_3, needs_reorder_77, bin_label_151


def test_restock_new_sku():
    stock = {}
    assert restock(stock, "A1", 5) == 5


def test_restock_existing_sku():
    stock = {"A1": 5}
    assert restock(stock, "A1", 3) == 8
    assert stock == {"A1": 8}


def test_boxes_needed_3():
    assert boxes_needed_3(*(740,)) == 25


def test_needs_reorder_77():
    assert needs_reorder_77(*(0,)) == True


def test_bin_label_151():
    assert bin_label_151(*(32, 5)) == 'QU-32-05'
