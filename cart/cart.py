"""Session helpers for the shopping cart."""

from decimal import Decimal

from products.models import Product


def get_cart(session):
    """Return the cart dictionary stored in the session."""
    cart = session.get("cart")
    if cart is None:
        cart = {}
        session["cart"] = cart
    return cart


def add_to_cart(session, product_id):
    """Add a product to the cart as a single purchase."""
    try:
        Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return False

    cart = get_cart(session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        return "already_in_cart"

    cart[product_id_str] = 1
    session.modified = True
    return True


def remove_from_cart(session, product_id):
    """Remove a product from the cart."""
    cart = get_cart(session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        session.modified = True
        return True

    return False


def get_cart_items(session):
    """Return cart items with product data."""
    cart = get_cart(session)
    items = []

    for product_id_str in cart.keys():
        try:
            product_id = int(product_id_str)
        except (TypeError, ValueError):
            continue

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        items.append({"product": product})

    return items


def get_cart_total(session, cart_items=None):
    """Return the total value of the cart."""
    total = Decimal("0.00")
    items = cart_items if cart_items is not None else get_cart_items(session)
    for item in items:
        total += item["product"].price
    return total


def clear_cart(session):
    """Clear all cart items from the session."""
    session["cart"] = {}
    session.modified = True
