def add_item(item, cart=[]):
    """Add an item to a cart and return the cart. Starts a new cart if none is given."""
    cart.append(item)
    return cart
