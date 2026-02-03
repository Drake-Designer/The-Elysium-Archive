"""Views for the reviews app."""

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import verified_email_required
from orders.models import AccessEntitlement
from products.models import Product

from .forms import ReviewForm
from .models import Review


def _user_has_entitlement(user, product) -> bool:
    """Check if the user has purchased the given product."""
    return AccessEntitlement.objects.filter(user=user, product=product).exists()


@verified_email_required
@require_http_methods(["POST"])
def create_review(request, slug):
    """Create a review for a purchased product."""
    product = get_object_or_404(Product, slug=slug, is_removed=False)

    if not _user_has_entitlement(request.user, product):
        messages.error(request, "You must purchase this archive to leave a review.")
        return redirect("product_detail", slug=slug)

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

    messages.error(request, "Please correct the errors in your review.")
    return redirect("product_detail", slug=slug)


@verified_email_required
@require_http_methods(["GET", "POST"])
def edit_review(request, slug, review_id):
    """Edit an existing review for a purchased product."""
    product = get_object_or_404(Product, slug=slug, is_removed=False)
    review = get_object_or_404(Review, id=review_id, product=product, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated.")
            return redirect("product_detail", slug=slug)
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
    product = get_object_or_404(Product, slug=slug, is_removed=False)
    review = get_object_or_404(Review, id=review_id, product=product, user=request.user)

    review.delete()
    messages.success(request, "Your review has been deleted.")
    return redirect("product_detail", slug=slug)
