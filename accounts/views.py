"""Views for accounts app."""

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from orders.models import AccessEntitlement, Order, OrderLineItem
from reviews.models import Review

from .forms import UserProfileForm
from .models import UserProfile

def _verified_or_redirect(request):
    if not has_verified_email(request.user):
        messages.warning(request, "Please verify your email before continuing.")
        return redirect("account_email")
    return None

def _dashboard_url_with_tab(tab_name):
    base_url = reverse("account_dashboard")
    return f"{base_url}?tab={tab_name}"

@login_required
@require_http_methods(["GET", "POST"])
def dashboard(request):
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    profile, _created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save(commit=False)

            remove_picture = form.cleaned_data.get("remove_picture")
            if remove_picture:
                profile.profile_picture = None

            profile.save()
            messages.success(request, "Your profile has been updated.")
            return redirect(_dashboard_url_with_tab("profile"))

        messages.error(request, "Please correct the errors below.")
        active_tab = "profile"
    else:
        form = UserProfileForm(instance=profile)

        requested_tab = (request.GET.get("tab") or "").strip().lower()
        tab_map = {
            "profile": "profile",
            "archive": "archive",
            "my-archive": "archive",
            "my_archive": "archive",
            "orders": "orders",
            "my-orders": "orders",
            "my_orders": "orders",
            "reviews": "reviews",
            "my-reviews": "reviews",
            "my_reviews": "reviews",
            "delete": "delete",
        }
        active_tab = tab_map.get(requested_tab, "profile")

    entitlements = (
        AccessEntitlement.objects.filter(user=request.user)
        .select_related("product")
        .order_by("-granted_at")
    )

    unlocked_products = [
        {"product": e.product, "purchase_date": e.granted_at} for e in entitlements
    ]

    line_items_qs = OrderLineItem.objects.select_related("product")
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related(Prefetch("line_items", queryset=line_items_qs))
        .order_by("-created_at")
    )

    reviews = (
        Review.objects.filter(user=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    # Build a dict for quick lookup of user reviews by product ID
    user_reviews_by_product = {review.product_id: review for review in reviews}

    context = {
        "active_tab": active_tab,
        "form": form,
        "unlocked_products": unlocked_products,
        "orders": orders,
        "reviews": reviews,
        "user_reviews_by_product": user_reviews_by_product,
    }
    return render(request, "accounts/dashboard.html", context)

@login_required
def my_archive(request):
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    return redirect(_dashboard_url_with_tab("archive"))

@login_required
def my_orders(request):
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    return redirect(_dashboard_url_with_tab("orders"))

@login_required
def my_reviews(request):
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    return redirect(_dashboard_url_with_tab("reviews"))

@login_required
@require_http_methods(["GET"])
def profile(request):
    """Redirect to dashboard profile tab."""
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    return redirect(_dashboard_url_with_tab("profile"))

@login_required
@require_http_methods(["GET", "POST"])
def delete_account(request):
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    if request.method == "POST":
        if request.user.is_superuser:
            messages.error(
                request,
                "Superuser accounts cannot be deleted from the site.",
            )
            return redirect("account_dashboard")

        request.user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home")

    return render(request, "accounts/delete_account.html")
