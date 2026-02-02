"""Views for checkout and Stripe integration."""

from datetime import timedelta

import stripe

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.decorators import verified_email_required
from cart.cart import clear_cart, get_cart_items, get_cart_total
from orders.models import AccessEntitlement, Order, OrderLineItem
from orders.services import grant_entitlements_for_order
from products.models import Product

def _set_stripe_key() -> bool:
    """Set Stripe API key from settings and return True if available."""
    if not getattr(settings, "STRIPE_SECRET_KEY", ""):
        return False
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return True

def _remove_purchased_from_session_cart(request, product_ids):
    """Remove purchased product IDs from the session cart."""
    cart = request.session.get("cart", {})
    if not cart:
        return 0

    removed = 0
    for pid in product_ids:
        pid_str = str(pid)
        if pid_str in cart:
            cart.pop(pid_str, None)
            removed += 1

    if removed:
        request.session["cart"] = cart
        request.session.modified = True

    return removed

def _get_recent_pending_order_any(request, minutes=15):
    """Return a recent pending order for the user, even without Stripe session id."""
    cutoff = timezone.now() - timedelta(minutes=minutes)
    return (
        Order.objects.filter(
            user=request.user,
            status="pending",
            created_at__gte=cutoff,
        )
        .order_by("-created_at")
        .first()
    )

def _try_reuse_stripe_session(request, order):
    """Reuse an existing Stripe session if it is still open."""
    try:
        session = stripe.checkout.Session.retrieve(order.stripe_session_id)
    except stripe.error.StripeError:
        return None

    session_status = session.get("status")
    payment_status = session.get("payment_status")
    session_url = session.get("url")

    if payment_status == "paid":
        return redirect(
            reverse("checkout_success", kwargs={"order_number": order.order_number})
        )

    if session_status == "open" and session_url:
        messages.info(request, "You already have an active checkout session.")
        return redirect(session_url, code=303)

    if session_status in ("expired", "complete"):
        order.status = "failed"
        order.save(update_fields=["status", "updated_at"])

    return None

def _fail_recent_pending_order(request, minutes=30):
    """Mark a recent pending order as failed."""
    cutoff = timezone.now() - timedelta(minutes=minutes)
    order = (
        Order.objects.filter(
            user=request.user,
            status="pending",
            stripe_session_id__isnull=False,
            created_at__gte=cutoff,
        )
        .exclude(stripe_session_id="")
        .order_by("-created_at")
        .first()
    )
    if not order:
        return None

    order.status = "failed"
    order.save(update_fields=["status", "updated_at"])
    return order

def _fail_stale_pending_orders(request, minutes=30):
    """Mark stale pending orders for the current user as failed."""
    cutoff = timezone.now() - timedelta(minutes=minutes)
    Order.objects.filter(
        user=request.user,
        status="pending",
        created_at__lt=cutoff,
    ).update(status="failed")

def _verify_and_finalize_order_if_paid(user, order):
    """Verify Stripe session and finalize order if Stripe reports paid."""
    if order.status != "pending":
        return False

    if not order.stripe_session_id:
        return False

    if not stripe.api_key:
        return False

    try:
        session = stripe.checkout.Session.retrieve(order.stripe_session_id)
    except stripe.error.StripeError:
        return False

    payment_status = (
        getattr(session, "payment_status", None) or session.get("payment_status")
    )

    if payment_status != "paid":
        return False

    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)
        if locked.status != "pending":
            return True

        locked.status = "paid"
        locked.stripe_payment_intent_id = session.get("payment_intent") or ""
        locked.save(update_fields=["status", "stripe_payment_intent_id", "updated_at"])

        grant_entitlements_for_order(locked, user=user)

    return True

@verified_email_required
@require_http_methods(["POST"])
def checkout(request):
    """Create Stripe checkout session and redirect user to payment."""
    if not _set_stripe_key():
        messages.error(request, "Payment is not configured yet. Please try again later.")
        return redirect("cart")

    _fail_stale_pending_orders(request)

    cart_items = get_cart_items(request.session)
    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    cart_products = [item["product"] for item in cart_items]
    cart_product_pks = [p.pk for p in cart_products]

    purchased_ids = set(
        AccessEntitlement.objects.filter(
            user=request.user,
            product_id__in=cart_product_pks,
        ).values_list("product_id", flat=True)
    )

    if purchased_ids:
        _remove_purchased_from_session_cart(request, purchased_ids)
        messages.info(
            request,
            "Your cart was updated because some items were already purchased.",
        )
        cart_products = [p for p in cart_products if p.pk not in purchased_ids]

    if not cart_products:
        messages.info(request, "You already own everything that was in your cart.")
        clear_cart(request.session)
        return redirect("cart")

    valid_products = list(
        Product.objects.filter(
            pk__in=[p.pk for p in cart_products],
            is_active=True,
            is_removed=False,
        )
    )
    if not valid_products:
        messages.warning(request, "Your cart is empty.")
        clear_cart(request.session)
        return redirect("cart")

    total = get_cart_total(request.session, [{"product": p} for p in valid_products])

    with transaction.atomic():
        existing_pending = _get_recent_pending_order_any(request)
        if existing_pending:
            locked = Order.objects.select_for_update().get(pk=existing_pending.pk)
            if locked.status == "pending" and locked.stripe_session_id:
                reused = _try_reuse_stripe_session(request, locked)
                if reused:
                    return reused
            order = locked
        else:
            order = Order.objects.create(
                user=request.user,
                total=total,
                status="pending",
            )

        if order.line_items.exists():
            order.line_items.all().delete()

        stripe_line_items = []
        for product in valid_products:
            discounted_price = product.get_discounted_price()

            OrderLineItem.objects.create(
                order=order,
                product=product,
                product_title=product.title,
                product_price=discounted_price,
                quantity=1,
                line_total=discounted_price,
            )

            stripe_line_items.append(
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": product.title,
                            "description": product.tagline or "",
                        },
                        "unit_amount": int(discounted_price * 100),
                    },
                    "quantity": 1,
                }
            )

    try:
        session = stripe.checkout.Session.create(
            line_items=stripe_line_items,
            mode="payment",
            success_url=request.build_absolute_uri(
                reverse("checkout_success", kwargs={"order_number": order.order_number})
            ),
            cancel_url=request.build_absolute_uri(reverse("checkout_cancel")),
            client_reference_id=order.order_number,
            metadata={
                "order_id": str(order.id),
                "order_number": order.order_number,
            },
        )

        order.stripe_session_id = session.id
        order.save(update_fields=["stripe_session_id", "updated_at"])

        if session.url:
            return redirect(session.url, code=303)

        raise ValueError("Stripe session URL is missing.")

    except Exception as exc:
        messages.error(
            request, f"Payment initialization failed: {exc}. Please try again."
        )

        try:
            order.status = "failed"
            order.save(update_fields=["status", "updated_at"])
        except Exception:
            pass

        return redirect("cart")

@verified_email_required
@require_http_methods(["GET"])
def checkout_success(request, order_number):
    """Display order confirmation after successful payment."""
    stripe_ready = _set_stripe_key()
    if not stripe_ready:
        messages.warning(
            request,
            "Payment verification is not available right now. Please refresh in a moment.",
        )

    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("archive")

    if order.status == "paid":
        grant_entitlements_for_order(order, user=request.user)
        clear_cart(request.session)
        return render(request, "checkout/success.html", {"order": order})

    if stripe_ready and order.status == "pending":
        paid_now = _verify_and_finalize_order_if_paid(request.user, order)
        if paid_now:
            order.refresh_from_db()
            clear_cart(request.session)

    return render(request, "checkout/success.html", {"order": order})

@verified_email_required
@require_http_methods(["GET"])
def checkout_status(request, order_number):
    """Return order status as JSON and finalize if Stripe reports paid."""
    stripe_ready = _set_stripe_key()

    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({"error": "not_found"}, status=404)

    if stripe_ready and order.status == "pending":
        paid_now = _verify_and_finalize_order_if_paid(request.user, order)
        if paid_now:
            order.refresh_from_db()

    return JsonResponse({"status": order.status})

@verified_email_required
def checkout_cancel(request):
    """Display cancellation message when user cancels payment."""
    _fail_recent_pending_order(request)
    messages.info(request, "Payment was cancelled. Your cart is still available.")
    return render(request, "checkout/cancel.html")
