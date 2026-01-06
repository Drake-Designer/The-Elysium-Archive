"""Shared utility functions for access control and entitlements."""

from orders.models import AccessEntitlement


def user_has_access(user, product):
    """Check if a user has purchased and has access to a product.

    Returns True if user has an AccessEntitlement for the product.
    Superusers always have access to all products.
    """
    if not user.is_authenticated:
        return False

    # Superusers have access to everything
    if user.is_superuser:
        return True

    return AccessEntitlement.objects.filter(user=user, product=product).exists()
