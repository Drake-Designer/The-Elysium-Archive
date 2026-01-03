from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from .cart import (
    add_to_cart as add_product_to_cart,
    get_cart_items,
    get_cart_total,
    remove_from_cart as remove_product_from_cart,
)


def add_to_cart(request):
    """Add a product to the shopping cart (session-based)."""
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        # Get product for message (validate exists and is active)
        product = get_object_or_404(Product, id=product_id, is_active=True)

        # Add to cart using helper function
        if add_product_to_cart(request.session, product_id, quantity):
            messages.success(
                request,
                f"✓ {product.title} added to cart!",
            )
        else:
            messages.error(
                request,
                f"Could not add {product.title} to cart.",
            )

        # Redirect back to product detail
        return redirect("product_detail", slug=product.slug)

    # If not POST, redirect to archive
    return redirect("archive")


def cart_view(request):
    """Display the shopping cart with items and totals."""
    context = {
        "cart_items": get_cart_items(request.session),
        "cart_total": get_cart_total(request.session),
    }
    return render(request, "cart/cart.html", context)


def remove_from_cart(request):
    """Remove a product from the shopping cart."""
    if request.method == "POST":
        product_id = request.POST.get("product_id")

        # Get product for message
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect("cart")

        # Remove from cart using helper function
        if remove_product_from_cart(request.session, product_id):
            messages.success(
                request,
                f"✓ {product.title} removed from cart.",
            )
        else:
            messages.info(request, f"{product.title} was not in your cart.")

    # Redirect back to cart view
    return redirect("cart")
