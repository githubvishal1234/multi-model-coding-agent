def add_item(item, cart=None):
    """Add an item to a cart and return the cart. Starts a new cart if none is given."""
    if cart is None:
        cart = []
    cart.append(item)
    return cart
