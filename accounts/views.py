"""Views for accounts app - profile management, My Archive, and account deletion."""

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm


@login_required
def my_archive(request):
    """Display user's unlocked archive entries (purchased products)."""
    unlocked_products = []

    # Try to find purchased products through multiple possible paths
    try:
        # Try OrderLineItem approach (if orders app has it)
        from orders.models import OrderLineItem

        line_items = OrderLineItem.objects.filter(
            order__user=request.user,
            order__status="completed",
        ).select_related("product")
        unlocked_products = [item.product for item in line_items]
    except (ImportError, AttributeError):
        # OrderLineItem doesn't exist or structure is different
        pass

    # If still empty, try looking for an AccessEntitlement model
    if not unlocked_products:
        try:
            from products.models import AccessEntitlement

            entitlements = AccessEntitlement.objects.filter(
                user=request.user
            ).select_related("product")
            unlocked_products = [e.product for e in entitlements]
        except (ImportError, AttributeError):
            # AccessEntitlement doesn't exist
            pass

    context = {
        "unlocked_products": unlocked_products,
    }
    return render(request, "accounts/my_archive.html", context)


@login_required
def profile(request):
    """Edit user profile (display name)."""
    user_profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            user_profile.display_name = form.cleaned_data["display_name"]
            user_profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("account_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(initial={"display_name": user_profile.display_name})

    context = {
        "form": form,
        "user_profile": user_profile,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def account_delete(request):
    """Confirm and delete user account."""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.info(
            request,
            "Your account has been deleted. We're sorry to see you go.",
        )
        return redirect("home")

    # GET: show confirmation page
    return render(request, "accounts/account_confirm_delete.html")
