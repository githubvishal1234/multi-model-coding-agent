from cart import add_item


def test_add_to_existing_cart():
    assert add_item("pen", ["book"]) == ["book", "pen"]
