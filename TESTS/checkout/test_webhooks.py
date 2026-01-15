import json
from unittest.mock import patch

import pytest
from django.urls import reverse

from orders.models import AccessEntitlement, Order, OrderLineItem
from products.models import Product


@pytest.mark.django_db
def test_webhook_idempotent_paid_event_does_not_duplicate_entitlements(
    client, verified_user
):
    """
    Ensure sending the same paid webhook twice does not duplicate entitlements.
    """
    user = verified_user
    client.force_login(user)

    product = Product.objects.create(
        title="Idempotent Archive",
        slug="idempotent-archive",
        price="9.99",
        is_active=True,
        tagline="Test tagline",
        description="Test description",
        content="Test content",
    )

    order = Order.objects.create(user=user, total="9.99", status="pending")
    OrderLineItem.objects.create(
        order=order,
        product=product,
        product_title=product.title,
        product_price=product.price,
        quantity=1,
        line_total=product.price,
    )

    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_idempotent",
                "payment_status": "paid",
                "payment_intent": "pi_test_idempotent",
                "metadata": {
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                },
            }
        },
    }

    with patch("checkout.webhooks.stripe.Webhook.construct_event", return_value=payload):
        response1 = client.post(
            reverse("stripe_webhook"),
            data=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )
        response2 = client.post(
            reverse("stripe_webhook"),
            data=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_signature",
        )

    assert response1.status_code == 200
    assert response2.status_code == 200

    order.refresh_from_db()
    assert order.status == "paid"

    # Must still be exactly one entitlement for this user+product
    assert AccessEntitlement.objects.filter(user=user, product=product).count() == 1
