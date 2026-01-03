"""Helper functions for creating and managing orders."""

from decimal import Decimal

from cart.cart import clear_cart, get_cart_items

from .models import Order, OrderLineItem


def create_order_from_cart(session, user=None):
    """Create an order from the current cart session."""
    cart_items = get_cart_items(session)

    if not cart_items:
        return None

    order = Order.objects.create(user=user)

    order_total = Decimal("0.00")

    for item in cart_items:
        line_item = OrderLineItem.objects.create(
            order=order,
            product=item["product"],
            product_title=item["product"].title,
            product_price=item["product"].price,
            quantity=1,
        )
        order_total += line_item.line_total

    order.total = order_total
    order.save()

    clear_cart(session)

    return order
