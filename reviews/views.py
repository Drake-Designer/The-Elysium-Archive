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


@verified_email_required
@require_http_methods(["GET", "POST"])
def edit_review(request, slug, review_id):
    """Edit an existing review for a purchased product."""
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect("archive")

    # Get review and verify ownership
    try:
        review = Review.objects.get(id=review_id, user=request.user, product=product)
    except Review.DoesNotExist:
        messages.error(
            request, "Review not found or you don't have permission to edit it."
        )
        return redirect("product_detail", slug=slug)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated.")
            return redirect("product_detail", slug=slug)
        else:
            messages.error(request, "Please correct the errors in your review.")
    else:
        form = ReviewForm(instance=review)

    context = {
        "form": form,
        "product": product,
        "review": review,
        "is_edit": True,
    }
    return render(request, "reviews/edit_review.html", context)


@verified_email_required
@require_http_methods(["POST"])
def delete_review(request, slug, review_id):
    """Delete an existing review."""
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect("archive")

    # Get review and verify ownership
    try:
        review = Review.objects.get(id=review_id, user=request.user, product=product)
        review.delete()
        messages.success(request, "Your review has been deleted.")
    except Review.DoesNotExist:
        messages.error(
            request, "Review not found or you don't have permission to delete it."
        )

    return redirect("product_detail", slug=slug)
