"""Views for checkout and Stripe integration."""

from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

import stripe

from accounts.decorators import verified_email_required
from cart.cart import clear_cart, get_cart_items, get_cart_total
from orders.models import AccessEntitlement, Order, OrderLineItem
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


def _get_recent_pending_order(request, minutes=15):
    """Return a recent pending order with a Stripe session id, if any."""
    cutoff = timezone.now() - timedelta(minutes=minutes)
    return (
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


def _try_reuse_stripe_session(request, order):
    """Reuse an existing Stripe session if it is still open."""
    try:
        session = stripe.checkout.Session.retrieve(order.stripe_session_id)
    except stripe.error.StripeError:
        return None

    session_status = session.get("status")
    payment_status = session.get("payment_status")
    session_url = session.get("url")

    # If Stripe says paid, send user to success page.
    if payment_status == "paid":
        return redirect(
            reverse("checkout_success", kwargs={"order_number": order.order_number})
        )

    # If the session is still open, reuse it.
    if session_status == "open" and session_url:
        messages.info(request, "You already have an active checkout session.")
        return redirect(session_url, code=303)

    # If the session is not usable anymore, mark the order as failed.
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


@verified_email_required
@require_http_methods(["POST"])
def checkout(request):
    """Create Stripe checkout session and redirect user to payment."""
    if not _set_stripe_key():
        messages.error(request, "Payment is not configured yet. Please try again later.")
        return redirect("cart")

    # Reuse a recent pending order if possible.
    recent_order = _get_recent_pending_order(request)
    if recent_order:
        reused = _try_reuse_stripe_session(request, recent_order)
        if reused:
            return reused

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

    # Ensure products still exist and are active.
    valid_products = list(Product.objects.filter(pk__in=[p.pk for p in cart_products], is_active=True))
    if not valid_products:
        messages.warning(request, "Your cart is empty.")
        clear_cart(request.session)
        return redirect("cart")

    total = get_cart_total(request.session, [{"product": p} for p in valid_products])
    order = Order.objects.create(
        user=request.user,
        total=total,
        status="pending",
    )

    line_items = []
    for product in valid_products:
        OrderLineItem.objects.create(
            order=order,
            product=product,
            product_title=product.title,
            product_price=product.price,
            quantity=1,
            line_total=product.price,
        )

        line_items.append(
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": product.title,
                        "description": product.tagline or "",
                    },
                    "unit_amount": int(product.price * 100),
                },
                "quantity": 1,
            }
        )

    try:
        session = stripe.checkout.Session.create(
            line_items=line_items,
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
        order.delete()
        return redirect("cart")


@verified_email_required
def checkout_success(request, order_number):
    """Display order confirmation after successful payment."""
    if not _set_stripe_key():
        messages.warning(
            request,
            "Payment verification is not available right now. Please refresh in a moment.",
        )

    try:
        order = Order.objects.get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("product_list")

    # If webhook already marked it as paid, we still must clear the cart
    # and ensure entitlements exist.
    if order.status == "paid":
        for line_item in order.line_items.select_related("product").all():
            if line_item.product:
                AccessEntitlement.objects.get_or_create(
                    user=request.user,
                    product=line_item.product,
                    defaults={"order": order},
                )
        clear_cart(request.session)
        context = {"order": order}
        return render(request, "checkout/success.html", context)

    # Fallback: if webhook did not arrive yet, verify via Stripe session.
    if order.status == "pending" and order.stripe_session_id and stripe.api_key:
        try:
            session = stripe.checkout.Session.retrieve(order.stripe_session_id)
            if session.payment_status == "paid":
                order.status = "paid"
                order.stripe_payment_intent_id = session.get("payment_intent") or ""
                order.save(
                    update_fields=["status", "stripe_payment_intent_id", "updated_at"]
                )

                for line_item in order.line_items.select_related("product").all():
                    if line_item.product:
                        AccessEntitlement.objects.get_or_create(
                            user=request.user,
                            product=line_item.product,
                            defaults={"order": order},
                        )

                clear_cart(request.session)

        except stripe.error.StripeError:
            messages.info(
                request,
                "Your payment is being confirmed. If this page still shows pending, refresh in a moment.",
            )

    context = {"order": order}
    return render(request, "checkout/success.html", context)


@verified_email_required
def checkout_cancel(request):
    """Display cancellation message when user cancels payment."""
    _fail_recent_pending_order(request)
    messages.info(request, "Payment was cancelled. Your cart is still available.")
    return render(request, "checkout/cancel.html")
