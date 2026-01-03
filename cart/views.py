from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from products.models import Product

from .cart import (
    add_to_cart as add_product_to_cart,
    get_cart_items,
    get_cart_total,
    remove_from_cart as remove_product_from_cart,
)


def _parse_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def add_to_cart(request):
    """Add a product to the shopping cart."""
    if request.method != "POST":
        return redirect("archive")

    product_id = _parse_int(request.POST.get("product_id"), None)
    if product_id is None:
        messages.error(request, "Product not found.")
        return redirect("archive")

    quantity = _parse_int(request.POST.get("quantity"), 1)
    if quantity < 1:
        quantity = 1

    product = get_object_or_404(Product, id=product_id, is_active=True)
    if add_product_to_cart(request.session, product_id, quantity):
        messages.success(request, f"V {product.title} added to cart!")
    else:
        messages.error(request, f"Could not add {product.title} to cart.")

    return redirect("product_detail", slug=product.slug)


def cart_view(request):
    """Render the shopping cart view."""
    cart_items = get_cart_items(request.session)
    context = {
        "cart_items": cart_items,
        "cart_total": get_cart_total(request.session, cart_items),
    }
    return render(request, "cart/cart.html", context)


def remove_from_cart(request):
    """Remove a product from the shopping cart."""
    if request.method != "POST":
        return redirect("cart")

    product_id = _parse_int(request.POST.get("product_id"), None)
    if product_id is None:
        messages.error(request, "Product not found.")
        return redirect("cart")

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect("cart")

    if remove_product_from_cart(request.session, product_id):
        messages.success(request, f"V {product.title} removed from cart.")
    else:
        messages.info(request, f"{product.title} was not in your cart.")

    return redirect("cart")
