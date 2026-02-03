"""Handle shopping cart interactions for authenticated users."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import verified_email_required
from orders.models import AccessEntitlement
from products.models import Product

from .cart import add_to_cart as add_product_to_cart
from .cart import (
    get_cart_items,
    get_cart_total,
)
from .cart import remove_from_cart as remove_product_from_cart


def _parse_int(value, default):
    """Parse an integer from input safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _remove_purchased_items_from_cart(request):
    """Remove already purchased products from the cart session."""
    cart = request.session.get("cart", {})
    if not cart:
        return 0

    try:
        product_ids = [int(pid) for pid in cart.keys()]
    except (TypeError, ValueError):
        return 0

    purchased_ids = set(
        AccessEntitlement.objects.filter(
            user=request.user,
            product_id__in=product_ids,
        ).values_list("product_id", flat=True)
    )

    removed = 0
    for pid in list(cart.keys()):
        try:
            if int(pid) in purchased_ids:
                cart.pop(pid, None)
                removed += 1
        except (TypeError, ValueError):
            continue

    if removed:
        request.session["cart"] = cart
        request.session.modified = True

    return removed


@verified_email_required
def add_to_cart(request):
    """Add a product to the shopping cart."""
    if request.method != "POST":
        return redirect("archive")

    product_id = _parse_int(request.POST.get("product_id"), None)
    if product_id is None:
        messages.error(request, "Product not found.")
        return redirect("archive")

    product = get_object_or_404(Product, id=product_id, is_active=True)

    if AccessEntitlement.objects.filter(user=request.user, product=product).exists():
        messages.info(request, "You already own this archive.")
        return redirect("product_detail", slug=product.slug)

    result = add_product_to_cart(request.session, product_id, user=request.user)

    if result is True:
        messages.success(request, f"✓ {product.title} added to cart!")
    elif result == "already_in_cart":
        messages.info(request, "This archive is already in your cart.")
    else:
        messages.error(request, f"Could not add {product.title} to cart.")

    return redirect("product_detail", slug=product.slug)


@verified_email_required
def cart_view(request):
    """Render the shopping cart view."""
    removed = _remove_purchased_items_from_cart(request)
    if removed:
        messages.info(
            request,
            "Your cart was updated because some items were already purchased.",
        )

    cart_items = get_cart_items(request.session, user=request.user)
    context = {
        "cart_items": cart_items,
        "cart_total": get_cart_total(request.session, cart_items),
    }
    return render(request, "cart/cart.html", context)


@verified_email_required
def remove_from_cart(request):
    """Remove a product from the shopping cart."""
    if request.method != "POST":
        return redirect("cart")

    product_id = _parse_int(request.POST.get("product_id"), None)
    if product_id is None:
        messages.error(request, "Product not found.")
        return redirect("cart")

    product = get_object_or_404(Product, id=product_id)

    if remove_product_from_cart(request.session, product_id, user=request.user):
        messages.success(request, f"✓ {product.title} removed from cart.")
    else:
        messages.info(request, f"{product.title} was not in your cart.")

    return redirect("cart")
