from unittest.mock import patch

import pytest
from django.urls import reverse

from orders.models import AccessEntitlement, Order, OrderLineItem
from products.models import Product


@pytest.mark.django_db
def test_checkout_success_fallback_marks_paid_and_grants_entitlements_when_stripe_paid(
    client, verified_user
):
    """
    Ensure success page fallback marks order as paid and grants entitlements
    when Stripe session reports payment_status paid.
    """
    user = verified_user
    client.force_login(user)

    product = Product.objects.create(
        title="Fallback Archive",
        slug="fallback-archive",
        price="9.99",
        is_active=True,
        tagline="Test tagline",
        description="Test description",
        content="Test content",
    )

    order = Order.objects.create(
        user=user,
        total="9.99",
        status="pending",
        stripe_session_id="cs_test_fallback",
    )
    OrderLineItem.objects.create(
        order=order,
        product=product,
        product_title=product.title,
        product_price=product.price,
        quantity=1,
        line_total=product.price,
    )

    # Put something in the cart to verify it gets cleared
    session = client.session
    session["cart"] = {str(product.pk): 1}
    session.save()

    fake_session = type(
        "FakeSession",
        (),
        {
            "payment_status": "paid",
            "get": lambda self, key, default=None: "pi_test_fallback"
            if key == "payment_intent"
            else default,
        },
    )()

    with patch("checkout.views._set_stripe_key", return_value=True):
        with patch("checkout.views.stripe.api_key", "sk_test_dummy"):
            with patch(
                "checkout.views.stripe.checkout.Session.retrieve",
                return_value=fake_session,
            ):
                response = client.get(
                    reverse(
                        "checkout_success",
                        kwargs={"order_number": order.order_number},
                    )
                )

    assert response.status_code == 200

    order.refresh_from_db()
    assert order.status == "paid"
    assert order.stripe_payment_intent_id == "pi_test_fallback"

    assert AccessEntitlement.objects.filter(user=user, product=product).exists()

    session = client.session
    assert session.get("cart", {}) == {}
