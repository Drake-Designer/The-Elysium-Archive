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


def add_to_cart(session, product_id, quantity=1):
    """Add a product to the cart or update its quantity."""
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return False

    if quantity < 1:
        return False

    try:
        Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return False

    cart = get_cart(session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity

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
    """Return cart items with product data and line totals."""
    cart = get_cart(session)
    items = []

    for product_id_str, quantity in cart.items():
        try:
            product_id = int(product_id_str)
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue

        if quantity < 1:
            continue

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        items.append(
            {
                "line_total": product.price * quantity,
                "product": product,
                "quantity": quantity,
            }
        )

    return items


def get_cart_total(session, cart_items=None):
    """Return the total value of the cart."""
    total = Decimal("0.00")
    items = cart_items if cart_items is not None else get_cart_items(session)
    for item in items:
        total += item["line_total"]
    return total


def update_cart_quantity(session, product_id, quantity):
    """Update the quantity of a product in the cart."""
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return False

    if quantity < 1:
        return False

    try:
        Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return False

    cart = get_cart(session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str] = quantity
        session.modified = True
        return True

    return False


def clear_cart(session):
    """Clear all cart items from the session."""
    session["cart"] = {}
    session.modified = True
