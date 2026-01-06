"""Views for the accounts app."""


from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from typing import Any


from .decorators import verified_email_required
from .forms import UserProfileForm
from .models import UserProfile



@verified_email_required
def dashboard(request):
    """Display user dashboard with purchased archives."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle profile form submission
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("account_dashboard")
    else:
        form = UserProfileForm(instance=profile)
    
    entitlements_data = []


    for entitlement in request.user.entitlements.select_related("product", "order"):
        product = entitlement.product
        order = entitlement.order
        if product:
            entitlements_data.append(
                {
                    "product": product,
                    "order": order,
                    "purchased_at": entitlement.granted_at,
                }
            )


    context: dict[str, Any] = {
        "entitlements": entitlements_data,
        "form": form,
        "profile": profile,
    }
    return render(request, "accounts/dashboard.html", context)



@verified_email_required
def my_archive(request):
    """Display user's purchased archives."""
    unlocked_products = []


    for entitlement in request.user.entitlements.select_related("product", "order"):
        product = entitlement.product
        # Only show active products (or products user owns even if inactive)
        if product and (product.is_active or True):
            unlocked_products.append(
                {
                    "product": product,
                    "purchase_date": entitlement.granted_at,
                }
            )


    context: dict[str, Any] = {
        "unlocked_products": unlocked_products,
    }
    return render(request, "accounts/my_archive.html", context)



@verified_email_required
def profile(request):
    """Display and edit user profile."""
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)


    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile_obj)


    context = {
        "form": form,
        "profile": profile_obj,
    }
    return render(request, "accounts/profile.html", context)



@login_required
@require_http_methods(["GET", "POST"])
def delete_account(request):
    """Handle account deletion with confirmation."""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(
            request, "Your account has been successfully deleted. We're sorry to see you go."
        )
        return redirect("home")

    return render(request, "accounts/account_confirm_delete.html")
