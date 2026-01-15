from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

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


@pytest.mark.django_db
def test_checkout_double_post_reuses_recent_pending_order_and_does_not_duplicate(
    client, verified_user
):
    """
    Ensure two checkout POSTs in quick succession do not create two pending orders.
    """
    user = verified_user
    client.force_login(user)

    product = Product.objects.create(
        title="Double Checkout Archive",
        slug="double-checkout-archive",
        price="9.99",
        is_active=True,
        tagline="Test tagline",
        description="Test description",
        content="Test content",
    )

    session = client.session
    session["cart"] = {str(product.pk): 1}
    session.save()

    fake_session_one = type(
        "FakeSession",
        (),
        {
            "id": "cs_test_double_1",
            "url": "https://stripe.test/checkout/cs_test_double_1",
        },
    )()

    fake_session_two = type(
        "FakeSession",
        (),
        {
            "id": "cs_test_double_2",
            "url": "https://stripe.test/checkout/cs_test_double_2",
        },
    )()

    with patch(
    "checkout.views.stripe.checkout.Session.create",
    side_effect=[fake_session_one, fake_session_two],
            ):

            response1 = client.post(reverse("checkout"))
            response2 = client.post(reverse("checkout"))

    assert response1.status_code in (302, 303)
    assert response2.status_code in (302, 303)

    pending_orders = Order.objects.filter(user=user, status="pending")
    assert pending_orders.count() == 1

    order = pending_orders.first()
    assert order is not None
    assert order.stripe_session_id in ("cs_test_double_1", "cs_test_double_2")

    assert OrderLineItem.objects.filter(order=order).count() == 1


@pytest.mark.django_db
def test_checkout_marks_stale_pending_orders_as_failed(client, verified_user):
    """
    Ensure stale pending orders are marked as failed when starting checkout.
    """
    user = verified_user
    client.force_login(user)

    product = Product.objects.create(
        title="Stale Pending Archive",
        slug="stale-pending-archive",
        price="9.99",
        is_active=True,
        tagline="Test tagline",
        description="Test description",
        content="Test content",
    )

    stale_order = Order.objects.create(
        user=user,
        total="9.99",
        status="pending",
    )

    Order.objects.filter(pk=stale_order.pk).update(
        created_at=timezone.now() - timedelta(hours=2)
    )

    session = client.session
    session["cart"] = {str(product.pk): 1}
    session.save()

    fake_session = type(
        "FakeSession",
        (),
        {
            "id": "cs_test_stale",
            "url": "https://stripe.test/checkout/cs_test_stale",
        },
    )()

    with patch("checkout.views._set_stripe_key", return_value=True):
        with patch(
            "checkout.views.stripe.checkout.Session.create",
            return_value=fake_session,
        ):
            response = client.post(reverse("checkout"))

    assert response.status_code in (302, 303)

    stale_order.refresh_from_db()
    assert stale_order.status == "failed"
