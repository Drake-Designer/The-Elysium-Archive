"""Views for checkout and Stripe integration."""

import os
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

import stripe

from accounts.decorators import verified_email_required
from cart.cart import clear_cart, get_cart_items, get_cart_total
from orders.models import AccessEntitlement, Order, OrderLineItem

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


@verified_email_required
@require_http_methods(["POST"])
def checkout(request):
    """Create Stripe checkout session and redirect user to payment."""
    cart_items = get_cart_items(request.session)

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    total = get_cart_total(request.session, cart_items)
    order = Order.objects.create(
        user=request.user,
        total=total,
        status="pending",
    )

    line_items = []
    for item in cart_items:
        product = item["product"]

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

        raise Exception("Stripe session URL is missing")

    except Exception as e:
        messages.error(
            request, f"Payment initialization failed: {str(e)}. Please try again."
        )
        order.delete()
        return redirect("cart")


@verified_email_required
def checkout_success(request, order_number):
    """Display order confirmation after successful payment."""
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

    # Fallback: if webhook did not arrive yet, verify via Stripe session
    if order.status == "pending" and order.stripe_session_id:
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
            pass

    context = {"order": order}
    return render(request, "checkout/success.html", context)


def checkout_cancel(request):
    """Display cancellation message when user cancels payment."""
    messages.info(request, "Payment was cancelled. Your cart is still available.")
    return render(request, "checkout/cancel.html")
