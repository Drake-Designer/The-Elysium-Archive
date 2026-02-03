"""Global context processors for templates."""

from __future__ import annotations

from cart.cart import get_cart, get_cart_items, get_cart_total


def cart_context(request):
    """Provide cart details and product IDs to templates."""
    try:
        cart_items = get_cart_items(request.session)
        cart_data = get_cart(request.session)
        cart_product_ids = set(cart_data.keys())
        cart_total = get_cart_total(request.session, cart_items)
        cart_count = len(cart_items)
    except Exception:  # noqa: BLE001
        cart_items = []
        cart_total = 0
        cart_count = 0
        cart_product_ids = set()

    return {
        "cart_items": cart_items,
        "cart_total": cart_total,
        "cart_count": cart_count,
        "cart_product_ids": cart_product_ids,
    }


def deals_context(request):
    """Add deal products to context for banner display."""
    try:
        from products.models import Product

        deal_products = Product.objects.filter(
            is_active=True, is_removed=False, is_deal=True
        ).select_related("category")[:10]
    except Exception:  # noqa: BLE001
        deal_products = []

    return {
        "deal_products": deal_products,
    }
