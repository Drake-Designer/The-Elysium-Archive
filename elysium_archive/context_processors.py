"""Global context processors for templates."""

from cart.cart import get_cart_items, get_cart_total


def cart_context(request):
    """Provide cart details to templates."""
    cart_items = get_cart_items(request.session)
    return {
        "cart_items": cart_items,
        "cart_total": get_cart_total(request.session, cart_items),
        "cart_count": len(cart_items),
    }
