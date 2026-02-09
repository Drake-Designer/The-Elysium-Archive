"""Service functions for orders and access entitlements."""

from __future__ import annotations

from django.db import transaction

from .models import AccessEntitlement, Order


def grant_entitlements_for_order(order: Order, user=None) -> int:
    """Grant access for each product in the order and return changed count."""
    if user is None:
        user = order.user

    if not user:
        return 0

    changed = 0

    with transaction.atomic():
        locked_order = Order.objects.select_for_update().get(pk=order.pk)

        for line_item in locked_order.line_items.select_related(
            "product"
        ).all():
            if not line_item.product:
                continue

            entitlement, created = AccessEntitlement.objects.get_or_create(
                user=user,
                product=line_item.product,
                defaults={"order": locked_order},
            )

            if created:
                changed += 1
                continue

            # Keep entitlement linked to paid order.
            if entitlement.order is None:
                entitlement.order = locked_order
                entitlement.save(update_fields=["order"])
                changed += 1

    return changed
