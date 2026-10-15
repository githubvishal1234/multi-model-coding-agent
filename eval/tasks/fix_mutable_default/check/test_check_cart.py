from cart import add_item


def test_new_cart_on_each_call():
    assert add_item("a") == ["a"]
    assert add_item("b") == ["b"]


def test_given_cart_is_extended_in_place():
    cart = ["book"]
    assert add_item("pen", cart) is cart
    assert cart == ["book", "pen"]


def test_given_empty_cart_is_used_not_replaced():
    cart = []
    assert add_item("x", cart) is cart
    assert cart == ["x"]
