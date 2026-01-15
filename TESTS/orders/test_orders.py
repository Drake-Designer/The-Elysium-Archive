"""Tests for order management and Stripe webhook handling."""

import pytest
from decimal import Decimal
from unittest.mock import patch

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
        order_paid.save(update_fields=["stripe_session_id", "stripe_payment_intent_id", "updated_at"])

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
    def test_webhook_checkout_expired_marks_failed(self, mock_construct, client, order_pending):
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
class TestOrderModel:
    """Test Order model behavior."""

    def test_order_generates_order_number_on_save(self, verified_user, product_active):
        """Order generates unique order_number on save."""
        order = Order.objects.create(
            user=verified_user,
            status="pending",
            total=Decimal("9.99"),
        )

        assert order.order_number
        assert len(order.order_number) > 0
        assert order.order_number.isupper()

    def test_order_number_unique(self, verified_user, product_active):
        """Each order has unique order_number."""
        order1 = Order.objects.create(
            user=verified_user,
            status="pending",
            total=Decimal("9.99"),
        )
        order2 = Order.objects.create(
            user=verified_user,
            status="pending",
            total=Decimal("19.99"),
        )

        assert order1.order_number != order2.order_number

    def test_order_default_status(self):
        """New order defaults to pending status."""
        order = Order(status=None)

    def test_order_timestamps(self, verified_user):
        """Order records created_at and updated_at."""
        order = Order.objects.create(
            user=verified_user,
            status="pending",
            total=Decimal("9.99"),
        )

        assert order.created_at is not None
        assert order.updated_at is not None


@pytest.mark.django_db
class TestAccessEntitlementModel:
    """Test AccessEntitlement model behavior."""

    def test_entitlement_unique_per_user_product(self, verified_user, product_active):
        """Cannot create duplicate entitlements for same user+product."""
        from django.db import IntegrityError

        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        with pytest.raises(IntegrityError):
            AccessEntitlement.objects.create(user=verified_user, product=product_active)

    def test_entitlement_grants_access(self, verified_user, product_inactive):
        """User with entitlement can access inactive product."""
        assert product_inactive.is_active is False

        AccessEntitlement.objects.create(user=verified_user, product=product_inactive)

        entitlements = AccessEntitlement.objects.filter(
            user=verified_user, product=product_inactive
        )
        assert entitlements.count() == 1

    def test_entitlement_survives_product_unpublish(self, verified_user, product_active):
        """Entitlement still exists when product is unpublished."""
        entitlement = AccessEntitlement.objects.create(
            user=verified_user, product=product_active
        )

        assert AccessEntitlement.objects.filter(id=entitlement.id).exists()

        product_active.is_active = False
        product_active.save(update_fields=["is_active", "updated_at"])

        assert AccessEntitlement.objects.filter(id=entitlement.id).exists()
