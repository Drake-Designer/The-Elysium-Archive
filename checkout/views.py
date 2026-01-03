"""Views for the checkout app."""

from decimal import Decimal

import stripe
from stripe import StripeError

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.decorators import verified_email_required
from cart.cart import clear_cart, get_cart_items, get_cart_total
from orders.models import Order, OrderLineItem
from products.models import Product

# Initialize Stripe with secret key from settings.
stripe.api_key = settings.STRIPE_SECRET_KEY


@verified_email_required
def checkout_view(request):
    """Build Stripe session and redirect to hosted checkout page."""
    cart_items = get_cart_items(request.session)

    # Validate cart is not empty.
    if not cart_items:
        messages.warning(request, "Your cart is empty. Add archives before checkout.")
        return redirect("cart")

    try:
        # Create pending Order record.
        order = Order.objects.create(
            user=request.user,
            status="pending",
            total=get_cart_total(request.session, cart_items),
        )

        # Create OrderLineItem records for each cart item.
        for item in cart_items:
            product = item["product"]
            OrderLineItem.objects.create(
                order=order,
                product=product,
                product_title=product.title,
                product_price=product.price,
                quantity=1,
            )

        # Build Stripe line items from cart.
        line_items = []
        for item in cart_items:
            product = item["product"]
            unit_amount_cents = int(product.price * 100)
            line_items.append(
                {
                    "price_data": {
                        "currency": "eur",
                        "unit_amount": unit_amount_cents,
                        "product_data": {
                            "name": product.title,
                            "description": product.tagline or "",
                            "metadata": {"product_id": str(product.pk)},
                        },
                    },
                    "quantity": 1,
                }
            )

        # Create Stripe Session with order metadata.
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            metadata={"order_id": str(order.pk)},
            success_url=request.build_absolute_uri(
                reverse("checkout_success") + f"?order_id={order.pk}"
            ),
            cancel_url=request.build_absolute_uri(reverse("checkout_cancel")),
        )

        # Handle missing session URL safely.
        if not session.url:
            messages.error(request, "Payment session could not be created. Try again.")
            return redirect("cart")

        # Redirect user to Stripe hosted checkout.
        return redirect(session.url)

    except Product.DoesNotExist:
        messages.error(request, "One or more items in your cart no longer exist.")
        clear_cart(request.session)
        return redirect("cart")

    except StripeError:
        messages.error(request, "Payment error occurred. Please try again.")
        return redirect("cart")

    except Exception:
        messages.error(request, "An error occurred during checkout. Please try again.")
        return redirect("cart")


@verified_email_required
def checkout_success(request):
    """Display order confirmation and clear cart on successful payment."""
    order_id = request.GET.get("order_id")

    # Redirect safely if order id is missing.
    if not order_id:
        messages.warning(request, "Order not found.")
        return redirect("home")

    # Retrieve order from database.
    try:
        order = Order.objects.get(pk=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.warning(request, "Order not found.")
        return redirect("home")

    # Update order status to completed.
    order.status = "completed"
    order.save()

    # Clear cart from session.
    clear_cart(request.session)

    # Show success message.
    messages.success(request, "Payment successful! Your archives are now unlocked.")

    context = {"order": order}
    return render(request, "checkout/checkout_success.html", context)


@verified_email_required
def checkout_cancel(request):
    """Display cancellation message and allow return to cart."""
    messages.info(request, "Checkout cancelled. Your cart is saved.")
    return render(request, "checkout/checkout_cancel.html")
