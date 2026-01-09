"""Global context processors for templates."""

from cart.cart import get_cart, get_cart_items, get_cart_total


def cart_context(request):
    """Provide cart details and product IDs to templates."""
    cart_items = get_cart_items(request.session)
    cart_data = get_cart(request.session)
    cart_product_ids = set(cart_data.keys())
    return {
        "cart_items": cart_items,
        "cart_total": get_cart_total(request.session, cart_items),
        "cart_count": len(cart_items),
        "cart_product_ids": cart_product_ids,
    }


def deals_context(request):
    """Add deal products to context for banner display."""
    from products.models import Product
    
    deal_products = Product.objects.filter(
        is_active=True,
        is_deal=True
    ).select_related("category")[:10]
    
    return {
        "deal_products": deal_products,
    }
