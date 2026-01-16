"""Handle Stripe webhook events for checkout."""

import logging

import stripe
from stripe import SignatureVerificationError

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import Order
from orders.services import grant_entitlements_for_order

logger = logging.getLogger(__name__)


def _set_stripe_key() -> bool:
    """Set Stripe API key from settings and return True if available."""
    if not getattr(settings, "STRIPE_SECRET_KEY", ""):
        return False
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return True


def _get_order_from_metadata(data):
    """Return order from Stripe metadata."""
    metadata = data.get("metadata", {}) if isinstance(data, dict) else {}

    order_id = metadata.get("order_id")
    if order_id:
        try:
            return Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return None

    # Backward compatible fallback if some sessions were created with order_number only
    order_number = metadata.get("order_number")
    if order_number:
        try:
            return Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return None

    return None


def _mark_order_paid(order, data):
    """Mark order as paid and store Stripe IDs."""
    payment_intent = data.get("payment_intent")
    session_id = data.get("id")

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)

        order.status = "paid"
        if payment_intent:
            order.stripe_payment_intent_id = payment_intent
        if session_id:
            order.stripe_session_id = session_id

        order.save(
            update_fields=[
                "status",
                "stripe_payment_intent_id",
                "stripe_session_id",
                "updated_at",
            ]
        )

        grant_entitlements_for_order(order)


def _ensure_paid_order_consistency(order, data):
    """Ensure a paid order has Stripe IDs and entitlements."""
    payment_intent = data.get("payment_intent")
    session_id = data.get("id")

    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order.pk)

        updated_fields = []

        if payment_intent and not order.stripe_payment_intent_id:
            order.stripe_payment_intent_id = payment_intent
            updated_fields.append("stripe_payment_intent_id")

        if session_id and not order.stripe_session_id:
            order.stripe_session_id = session_id
            updated_fields.append("stripe_session_id")

        if updated_fields:
            updated_fields.append("updated_at")
            order.save(update_fields=updated_fields)

        grant_entitlements_for_order(order)


def _handle_checkout_completed(data):
    """Handle checkout.session.completed event."""
    order = _get_order_from_metadata(data)
    if not order:
        logger.warning("Webhook missing order reference on checkout.session.completed")
        return

    # If already paid, only ensure consistency.
    if order.status == "paid":
        _ensure_paid_order_consistency(order, data)
        return

    # Do not grant access unless Stripe confirms the payment is paid.
    if data.get("payment_status") != "paid":
        logger.info(
            "Checkout completed but payment not paid yet (order=%s).",
            order.order_number,
        )

        session_id = data.get("id")
        if session_id:
            with transaction.atomic():
                locked = Order.objects.select_for_update().get(pk=order.pk)
                if not locked.stripe_session_id:
                    locked.stripe_session_id = session_id
                    locked.save(update_fields=["stripe_session_id", "updated_at"])
        return

    _mark_order_paid(order, data)


def _handle_async_payment_succeeded(data):
    """Handle checkout.session.async_payment_succeeded event."""
    order = _get_order_from_metadata(data)
    if not order:
        logger.warning(
            "Webhook missing order reference on checkout.session.async_payment_succeeded"
        )
        return

    if order.status == "paid":
        _ensure_paid_order_consistency(order, data)
        return

    if data.get("payment_status") == "paid":
        _mark_order_paid(order, data)


def _handle_checkout_expired(data):
    """Handle checkout.session.expired event."""
    order = _get_order_from_metadata(data)
    if not order:
        logger.warning("Webhook missing order reference on checkout.session.expired")
        return

    if order.status == "paid":
        return

    session_id = data.get("id")

    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)
        if locked.status == "paid":
            return

        locked.status = "failed"
        if session_id and not locked.stripe_session_id:
            locked.stripe_session_id = session_id

        locked.save(update_fields=["status", "stripe_session_id", "updated_at"])


def _handle_payment_failed(data):
    """Handle payment failure event."""
    order = _get_order_from_metadata(data)
    if not order:
        logger.warning("Webhook missing order reference on payment failure")
        return

    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)
        if locked.status == "paid":
            return

        locked.status = "failed"
        locked.save(update_fields=["status", "updated_at"])


@csrf_exempt
def stripe_webhook(request):
    """Process Stripe webhooks with signature verification."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if not _set_stripe_key():
        logger.error("Stripe secret key missing")
        return JsonResponse({"error": "Stripe not configured"}, status=500)

    endpoint_secret = settings.STRIPE_WH_SECRET
    if not endpoint_secret:
        logger.error("Stripe webhook secret missing")
        return JsonResponse({"error": "Webhook not configured"}, status=500)

    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    if not sig_header:
        logger.warning("Missing Stripe signature header")
        return JsonResponse({"error": "Missing signature"}, status=400)

    payload = request.body

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logger.warning("Invalid payload for Stripe webhook")
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except SignatureVerificationError:
        logger.warning("Invalid signature for Stripe webhook")
        return JsonResponse({"error": "Invalid signature"}, status=400)

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    try:
        if event_type == "checkout.session.completed":
            _handle_checkout_completed(data)
        elif event_type == "checkout.session.async_payment_succeeded":
            _handle_async_payment_succeeded(data)
        elif event_type == "checkout.session.expired":
            _handle_checkout_expired(data)
        elif event_type in (
            "payment_intent.payment_failed",
            "checkout.session.async_payment_failed",
        ):
            _handle_payment_failed(data)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error processing Stripe webhook: %s", exc)
        return JsonResponse({"error": "Webhook processing error"}, status=500)

    return JsonResponse({"status": "ok"})
