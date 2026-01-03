"""Account views for profiles, archives, and deletion."""

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, render

from .decorators import verified_email_required
from .forms import ProfileForm
from .models import UserProfile


@verified_email_required
def dashboard(request):
    """Render the account dashboard."""
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    unlocked_products = []

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile.display_name = form.cleaned_data["display_name"]

            # Handle profile picture removal
            if form.cleaned_data.get("remove_picture") and user_profile.profile_picture:
                user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
            # Handle profile picture upload
            elif form.cleaned_data.get("profile_picture"):
                if user_profile.profile_picture:
                    user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = form.cleaned_data["profile_picture"]

            user_profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("account_dashboard")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(initial={"display_name": user_profile.display_name})

    context = {
        "form": form,
        "unlocked_products": unlocked_products,
        "user_profile": user_profile,
    }
    return render(request, "accounts/dashboard.html", context)


@verified_email_required
def my_archive(request):
    """Render the user's unlocked archive entries."""
    context = {
        "unlocked_products": [],
    }
    return render(request, "accounts/my_archive.html", context)


@verified_email_required
def profile(request):
    """Render and update the user profile."""
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile.display_name = form.cleaned_data["display_name"]

            # Handle profile picture removal
            if form.cleaned_data.get("remove_picture") and user_profile.profile_picture:
                user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
            # Handle profile picture upload
            elif form.cleaned_data.get("profile_picture"):
                if user_profile.profile_picture:
                    user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = form.cleaned_data["profile_picture"]

            user_profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("account_profile")
        messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(initial={"display_name": user_profile.display_name})

    context = {
        "form": form,
        "user_profile": user_profile,
    }
    return render(request, "accounts/profile.html", context)


@verified_email_required
def account_delete(request):
    """Delete the current user account."""
    # Prevent superusers from deleting their accounts
    if request.user.is_superuser:
        messages.error(
            request,
            "Superuser accounts cannot be deleted. Contact system administrator.",
        )
        return redirect("account_profile")

    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.info(
            request,
            "Your account has been deleted. We're sorry to see you go.",
        )
        return redirect("home")

    return render(request, "accounts/account_confirm_delete.html")
