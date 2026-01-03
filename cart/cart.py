"""
Shopping cart session management and helper functions.
"""

from products.models import Product


def get_cart(session):
    """Retrieve the cart dictionary from session, create if missing."""
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]


def add_to_cart(session, product_id, quantity=1):
    """
    Add a product to the cart or update quantity if already present.

    Args:
        session: Django request.session
        product_id: ID of the product to add
        quantity: Number of items (default 1)

    Returns:
        bool: True if successful, False if product doesn't exist or is inactive
    """
    # Validate product exists and is active
    try:
        Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return False

    cart = get_cart(session)
    product_id_str = str(product_id)

    # Add or update quantity
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity

    session.modified = True
    return True


def remove_from_cart(session, product_id):
    """
    Remove a product from the cart entirely.

    Args:
        session: Django request.session
        product_id: ID of the product to remove

    Returns:
        bool: True if removed, False if product not in cart
    """
    cart = get_cart(session)
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        session.modified = True
        return True

    return False


def get_cart_items(session):
    """
    Retrieve cart items with product details and calculations.

    Returns:
        list: List of dicts with product info, quantity, and line_total
    """
    cart = get_cart(session)
    items = []

    for product_id_str, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id_str))
            line_total = product.price * quantity
            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "line_total": line_total,
                }
            )
        except Product.DoesNotExist:
            # Skip products that no longer exist
            continue

    return items


def get_cart_total(session):
    """
    Calculate the total price of all items in cart.

    Returns:
        Decimal: Total cart amount
    """
    from decimal import Decimal

    items = get_cart_items(session)
    total = Decimal("0.00")

    for item in items:
        total += item["line_total"]

    return total


def clear_cart(session):
    """Empty the entire shopping cart."""
    session["cart"] = {}
    session.modified = True
