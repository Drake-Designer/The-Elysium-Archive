"""Handle Stripe webhook events for checkout."""

import logging

import stripe
from stripe import SignatureVerificationError

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from orders.models import AccessEntitlement, Order

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def _get_order_from_metadata(data):
    """Return order from Stripe metadata."""
    metadata = data.get("metadata", {}) if isinstance(data, dict) else {}
    order_id = metadata.get("order_id")
    if not order_id:
        return None
    try:
        return Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return None


def _grant_entitlements(order):
    """Create entitlements for purchased products."""
    for line in order.line_items.select_related("product"):
        if not line.product:
            continue
        AccessEntitlement.objects.get_or_create(
            user=order.user,
            product=line.product,
            defaults={"order": order},
        )


def _handle_checkout_completed(data):
    """Handle checkout.session.completed event."""
    order = _get_order_from_metadata(data)
    if not order:
        logger.warning("Webhook missing order reference on checkout.session.completed")
        return

    payment_intent = data.get("payment_intent")
    session_id = data.get("id")

    order.status = "paid"
    if payment_intent:
        order.stripe_pid = payment_intent
    if session_id:
        order.stripe_session_id = session_id
    order.save(
        update_fields=["status", "stripe_pid", "stripe_session_id", "updated_at"]
    )

    _grant_entitlements(order)


def _handle_payment_failed(data):
    """Handle payment failure event."""
    order = _get_order_from_metadata(data)
    if not order:
        logger.warning("Webhook missing order reference on payment failure")
        return
    order.status = "failed"
    order.save(update_fields=["status", "updated_at"])


@csrf_exempt
def stripe_webhook(request):
    """Process Stripe webhooks with signature verification."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    endpoint_secret = settings.STRIPE_WH_SECRET
    if not endpoint_secret:
        logger.error("Stripe webhook secret missing")
        return JsonResponse({"error": "Webhook not configured"}, status=500)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

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
        elif event_type in (
            "payment_intent.payment_failed",
            "checkout.session.async_payment_failed",
        ):
            _handle_payment_failed(data)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error processing Stripe webhook: %s", exc)
        return JsonResponse({"error": "Webhook processing error"}, status=500)

    return JsonResponse({"status": "ok"})
