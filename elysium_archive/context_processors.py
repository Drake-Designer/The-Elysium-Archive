"""
Global context processors for all templates.
"""

from cart.cart import get_cart_items, get_cart_total


def cart_context(request):
    """
    Add cart data to all template contexts.

    Makes cart items and total available in every template
    without needing to pass them explicitly from views.
    """
    return {
        "cart_items": get_cart_items(request.session),
        "cart_total": get_cart_total(request.session),
        "cart_count": len(get_cart_items(request.session)),
    }
