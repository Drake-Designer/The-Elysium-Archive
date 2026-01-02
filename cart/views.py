from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product


def add_to_cart(request):
    """Add a product to the shopping cart (session-based)."""
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))

        # Validate product exists and is active
        product = get_object_or_404(Product, id=product_id, is_active=True)

        # Initialize cart in session if not exists
        if "cart" not in request.session:
            request.session["cart"] = {}

        cart = request.session["cart"]

        # Add or update product in cart
        if str(product_id) in cart:
            cart[str(product_id)]["quantity"] += quantity
        else:
            cart[str(product_id)] = {
                "title": product.title,
                "slug": product.slug,
                "price": float(product.price),
                "image_url": product.image.url if product.image else None,
                "quantity": quantity,
            }

        request.session.modified = True

        # Show success message
        messages.success(
            request,
            f"✓ {product.title} added to cart!",
        )

        # Redirect back to product detail
        return redirect("product_detail", slug=product.slug)

    # If not POST, redirect to archive
    return redirect("archive")
