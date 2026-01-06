"""Tests for checkout and order creation."""

import pytest
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch, MagicMock
from orders.models import Order, OrderLineItem
from stripe import StripeError


@pytest.mark.django_db
class TestCheckoutAccess:
    """Test checkout page access and email verification gate."""

    def test_unverified_user_cannot_checkout(
        self, client, unverified_user, product_active
    ):
        """Unverified user is redirected from checkout."""
        client.force_login(unverified_user)

        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})

        response = client.get(reverse("checkout"))

        assert response.status_code == 302
        assert reverse("account_email") in response.url

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_verified_user_can_access_checkout(
        self, mock_stripe_session, client, verified_user, product_active
    ):
        """Verified user can checkout and gets Stripe session redirect."""
        client.force_login(verified_user)

        mock_stripe_session.return_value = MagicMock(
            url="https://checkout.stripe.com/test123",
            id="cs_test123",
        )

        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})
        response = client.post(reverse("checkout"))

        assert response.status_code == 302
        assert response.url == "https://checkout.stripe.com/test123"

    def test_anonymous_user_redirects_to_login(self, client, product_active):
        """Anonymous user is redirected to login from checkout."""
        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})
        response = client.post(reverse("checkout"), follow=False)

        assert response.status_code == 302
        assert reverse("account_login") in response.url


@pytest.mark.django_db
class TestCheckoutOrderCreation:
    """Test order creation during checkout."""

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_checkout_creates_order(
        self, mock_stripe_session, verified_user, client, product_active
    ):
        """Checkout creates Order and OrderLineItem records."""
        client.force_login(verified_user)

        mock_stripe_session.return_value = MagicMock(
            url="https://checkout.stripe.com/test123",
            id="cs_test123",
        )

        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})

        assert Order.objects.filter(user=verified_user).count() == 0

        response = client.post(reverse("checkout"), follow=False)

        assert Order.objects.filter(user=verified_user).count() == 1
        order = Order.objects.get(user=verified_user)
        assert order.status == "pending"

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_checkout_creates_line_items(
        self, mock_stripe_session, verified_user, client, product_active
    ):
        """Checkout creates OrderLineItem for each cart item."""
        client.force_login(verified_user)

        mock_stripe_session.return_value = MagicMock(
            url="https://checkout.stripe.com/test123",
            id="cs_test123",
        )

        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})
        client.post(reverse("checkout"))

        order = Order.objects.get(user=verified_user)
        line_items = OrderLineItem.objects.filter(order=order)

        assert line_items.count() == 1

        line_item = line_items.first()
        assert line_item is not None
        assert line_item.product == product_active
        assert line_item.product_title == product_active.title
        assert line_item.product_price == product_active.price

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_checkout_sets_order_total(
        self, mock_stripe_session, verified_user, client, product_active
    ):
        """Checkout sets order total from cart."""
        client.force_login(verified_user)

        mock_stripe_session.return_value = MagicMock(
            url="https://checkout.stripe.com/test123",
            id="cs_test123",
        )

        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})
        client.post(reverse("checkout"))

        order = Order.objects.get(user=verified_user)
        assert order.total == product_active.price

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_checkout_redirects_to_stripe(
        self, mock_stripe_session, verified_user, client, product_active
    ):
        """Checkout redirects to Stripe session URL."""
        client.force_login(verified_user)

        stripe_url = "https://checkout.stripe.com/test123"
        mock_stripe_session.return_value = MagicMock(
            url=stripe_url,
            id="cs_test123",
        )

        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})
        response = client.post(reverse("checkout"), follow=False)

        assert response.status_code == 302
        assert stripe_url in response.url

    @patch("checkout.views.stripe.checkout.Session.create")
    def test_checkout_cleans_order_on_stripe_error(
        self, mock_stripe_session, verified_user, client, product_active
    ):
        """Checkout cleans up order records when Stripe session fails."""
        client.force_login(verified_user)
        mock_stripe_session.side_effect = StripeError("Stripe failure")

        client.post(reverse("add_to_cart"), {"product_id": str(product_active.id)})
        response = client.post(reverse("checkout"), follow=False)

        assert response.status_code == 302
        assert reverse("cart") in response.url
        assert Order.objects.filter(user=verified_user).count() == 0
        assert OrderLineItem.objects.count() == 0

    def test_checkout_empty_cart_shows_warning(self, client, verified_user):
        """Checkout with empty cart shows warning and redirects."""
        client.force_login(verified_user)

        response = client.post(reverse("checkout"), follow=True)

        assert response.status_code == 200
        assert reverse("cart") in response.request.get("PATH_INFO")


@pytest.mark.django_db
class TestCheckoutSuccess:
    """Test checkout success page."""

    def test_success_page_displays_order(self, client, verified_user, order_pending):
        """Success page shows order details."""
        client.force_login(verified_user)

        response = client.get(
            reverse("checkout_success", kwargs={"order_number": order_pending.order_number})
        )

        assert response.status_code == 200
        assert "checkout/success.html" in [t.name for t in response.templates]

    def test_success_page_updates_status_on_paid(
        self, client, verified_user, order_pending
    ):
        """Success page handles pending->paid transition."""
        client.force_login(verified_user)

        order_pending.status = "paid"
        order_pending.save()

        response = client.get(
            reverse("checkout_success", kwargs={"order_number": order_pending.order_number})
        )

        assert response.status_code == 200

    def test_success_page_wrong_user_404(
        self, client, verified_user, unverified_user, order_pending
    ):
        """Another user cannot view someone else's order success page."""
        other_user = unverified_user
        client.force_login(other_user)

        response = client.get(
            reverse("checkout_success", kwargs={"order_number": order_pending.order_number})
        )

        assert response.status_code in [302, 404]


@pytest.mark.django_db
class TestCheckoutCancel:
    """Test checkout cancellation."""

    def test_cancel_page_accessible(self, client, verified_user):
        """Cancel page is accessible."""
        client.force_login(verified_user)

        response = client.get(reverse("checkout_cancel"))

        assert response.status_code == 200
        assert "checkout/cancel.html" in [t.name for t in response.templates]

    def test_cancel_page_shows_message(self, client, verified_user):
        """Cancel page shows cancellation message."""
        client.force_login(verified_user)

        response = client.get(reverse("checkout_cancel"))

        messages = list(response.context.get("messages", []))
