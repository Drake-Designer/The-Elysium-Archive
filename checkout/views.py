"""Views for checkout and Stripe integration."""

import os
import stripe
from decimal import Decimal
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from accounts.decorators import verified_email_required
from cart.cart import get_cart_items, get_cart_total, clear_cart
from orders.models import AccessEntitlement, Order, OrderLineItem
from products.models import Product

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
            metadata={"order_number": order.order_number},
        )

        order.stripe_session_id = session.id
        order.save()

        if session.url:
            return redirect(session.url, code=303)
        else:
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

    if order.status == "pending" and order.stripe_session_id:
        try:
            session = stripe.checkout.Session.retrieve(order.stripe_session_id)
            if session.payment_status == "paid":
                order.status = "paid"
                order.save()

                for line_item in order.line_items.all():
                    if line_item.product:
                        AccessEntitlement.objects.get_or_create(
                            user=request.user, product=line_item.product, order=order
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


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events for payment processing."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_number = session.get("metadata", {}).get("order_number")

        if order_number:
            try:
                order = Order.objects.get(order_number=order_number)
                order.status = "paid"
                order.stripe_payment_intent_id = session.get("payment_intent")
                order.save()

                for line_item in order.line_items.all():
                    if line_item.product:
                        AccessEntitlement.objects.get_or_create(
                            user=order.user,
                            product=line_item.product,
                            order=order,
                        )

            except Order.DoesNotExist:
                return HttpResponse(status=404)

    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        try:
            order = Order.objects.get(stripe_payment_intent_id=payment_intent["id"])
            order.status = "failed"
            order.save()
        except Order.DoesNotExist:
            pass

    return JsonResponse({"status": "success"})
