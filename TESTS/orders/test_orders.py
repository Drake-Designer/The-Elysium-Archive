"""Tests for order management and Stripe webhook handling."""

from decimal import Decimal
from unittest.mock import patch

import pytest
from django.urls import reverse

from orders.models import AccessEntitlement, Order


@pytest.mark.django_db
class TestWebhookHandling:
    """Test Stripe webhook processing with mocked signature verification."""

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_checkout_completed_creates_entitlements(
        self, mock_construct, client, verified_user, order_pending
    ):
        """Webhook on checkout.session.completed creates AccessEntitlements."""
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "payment_intent": "pi_test123",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        assert AccessEntitlement.objects.filter(user=verified_user).count() == 0

        response = client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert response.status_code == 200

        entitlements = AccessEntitlement.objects.filter(user=verified_user)
        assert entitlements.count() == 1

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_updates_order_status(self, mock_construct, client, order_pending):
        """Webhook updates order status from pending to paid."""
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "payment_intent": "pi_test123",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        assert order_pending.status == "pending"

        client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        order_pending.refresh_from_db()
        assert order_pending.status == "paid"

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_stores_stripe_ids(self, mock_construct, client, order_pending):
        """Webhook stores Stripe session and payment intent IDs."""
        session_id = "cs_test123"
        payment_id = "pi_test123"

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": session_id,
                    "payment_intent": payment_id,
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        order_pending.refresh_from_db()
        assert order_pending.stripe_session_id == session_id
        assert order_pending.stripe_payment_intent_id == payment_id

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_idempotent_same_event_twice(
        self, mock_construct, client, verified_user, order_pending
    ):
        """Same webhook event twice creates only one AccessEntitlement (idempotent)."""
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "payment_intent": "pi_test123",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert AccessEntitlement.objects.filter(user=verified_user).count() == 1

        client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert AccessEntitlement.objects.filter(user=verified_user).count() == 1

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_checkout_completed_unpaid_does_not_grant_access(
        self, mock_construct, client, verified_user, order_pending
    ):
        """Checkout completed but unpaid does not grant access or mark as paid."""
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "payment_intent": "pi_test123",
                    "payment_status": "unpaid",
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        order_pending.refresh_from_db()
        assert order_pending.status == "pending"
        assert AccessEntitlement.objects.filter(user=verified_user).count() == 0

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_payment_failed_sets_status(
        self, mock_construct, client, order_pending
    ):
        """Webhook on payment failure sets order status to 'failed'."""
        mock_construct.return_value = {
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        order_pending.refresh_from_db()
        assert order_pending.status == "failed"

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_invalid_signature_rejected(
        self, mock_construct, client, order_pending
    ):
        """Webhook with invalid signature is rejected."""
        from stripe import SignatureVerificationError

        mock_construct.side_effect = SignatureVerificationError("Invalid", "sig")

        response = client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_sig",
        )

        assert response.status_code == 400

    def test_webhook_missing_signature_header_rejected(self, client):
        """Webhook without Stripe signature header is rejected."""
        response = client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_webhook_post_required(self, client):
        """Webhook only accepts POST, rejects GET."""
        response = client.get(reverse("stripe_webhook"))

        assert response.status_code == 405

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_missing_order_handled(self, mock_construct, client):
        """Webhook with missing order reference is handled gracefully."""
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "payment_intent": "pi_test123",
                    "payment_status": "paid",
                    "metadata": {"order_id": "99999"},
                }
            },
        }

        response = client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert response.status_code == 200

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_paid_order_does_not_duplicate_entitlements(
        self, mock_construct, client, verified_user, order_paid
    ):
        """Webhook on already paid order does not create duplicate entitlements."""
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test999",
                    "payment_intent": "pi_test999",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order_paid.id)},
                }
            },
        }

        assert AccessEntitlement.objects.filter(user=verified_user).count() == 1

        response = client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert response.status_code == 200
        assert AccessEntitlement.objects.filter(user=verified_user).count() == 1

        order_paid.refresh_from_db()
        assert order_paid.status == "paid"

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_paid_order_fills_missing_stripe_ids(
        self, mock_construct, client, order_paid
    ):
        """Paid order stores Stripe IDs if they are missing."""
        order_paid.stripe_session_id = ""
        order_paid.stripe_payment_intent_id = ""
        order_paid.save(
            update_fields=[
                "stripe_session_id",
                "stripe_payment_intent_id",
                "updated_at",
            ]
        )

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test999",
                    "payment_intent": "pi_test999",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order_paid.id)},
                }
            },
        }

        client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        order_paid.refresh_from_db()
        assert order_paid.stripe_session_id == "cs_test999"
        assert order_paid.stripe_payment_intent_id == "pi_test999"

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_order_without_user_does_not_crash(
        self, mock_construct, client, order_pending
    ):
        """Webhook does not crash if order has no user."""
        Order.objects.filter(pk=order_pending.pk).update(user=None)

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test123",
                    "payment_intent": "pi_test123",
                    "payment_status": "paid",
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        response = client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert response.status_code == 200
        assert AccessEntitlement.objects.count() == 0

        order_pending.refresh_from_db()
        assert order_pending.status == "paid"

    @patch("checkout.webhooks.stripe.Webhook.construct_event")
    def test_webhook_checkout_expired_marks_failed(
        self, mock_construct, client, order_pending
    ):
        """Webhook on checkout.session.expired marks order as failed."""
        mock_construct.return_value = {
            "type": "checkout.session.expired",
            "data": {
                "object": {
                    "id": "cs_test_expired",
                    "metadata": {"order_id": str(order_pending.id)},
                }
            },
        }

        response = client.post(
            reverse("stripe_webhook"),
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert response.status_code == 200
        order_pending.refresh_from_db()
        assert order_pending.status == "failed"


@pytest.mark.django_db
class TestOrdersDashboardTabs:
    """Test dashboard orders tab shortcuts."""

    def test_my_orders_redirects_to_dashboard_tab(self, client, verified_user):
        """My orders shortcut redirects to dashboard orders tab."""
        client.force_login(verified_user)
        response = client.get(reverse("my_orders"))
        assert response.status_code == 302
        assert reverse("account_dashboard") in response.url
        assert "tab=orders" in response.url
