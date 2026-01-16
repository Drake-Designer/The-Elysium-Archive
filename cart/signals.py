"""Signals for syncing persistent carts with the session."""

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Cart, CartItem


@receiver(user_logged_in)
def restore_cart_to_session(sender, request, user, **kwargs):
    """Restore a user's persistent cart into the session on login if the session cart is empty."""
    session_cart = request.session.get("cart", {})
    if session_cart:
        return

    cart, _ = Cart.objects.get_or_create(user=user)

    items = (
        CartItem.objects.filter(cart=cart)
        .select_related("product")
        .filter(product__is_active=True)
    )

    request.session["cart"] = {str(item.product.pk): 1 for item in items}
    request.session.modified = True
