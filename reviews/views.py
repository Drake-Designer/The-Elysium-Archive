"""Views for the reviews app."""

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import verified_email_required
from orders.models import AccessEntitlement
from products.models import Product

from .forms import ReviewForm
from .models import Review


@verified_email_required
@require_http_methods(["POST"])
def create_review(request, slug):
    """Create a review for a purchased product."""
    try:
        product = Product.objects.get(slug=slug, is_active=True)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect("archive")

    # Check if user has purchased this product.
    entitlement = AccessEntitlement.objects.filter(
        user=request.user, product=product
    ).first()
    if not entitlement:
        messages.error(request, "You must purchase this archive to leave a review.")
        return redirect("product_detail", slug=slug)

    # Check if user already reviewed this product.
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.info(request, "You have already reviewed this archive entry.")
        return redirect("product_detail", slug=slug)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        try:
            review.save()
            messages.success(request, "Your review has been submitted.")
        except IntegrityError:
            messages.info(request, "You have already reviewed this archive entry.")
        return redirect("product_detail", slug=slug)

    # If form invalid, redirect back with error.
    messages.error(request, "Please correct the errors in your review.")
    return redirect("product_detail", slug=slug)
