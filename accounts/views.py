"""Views for accounts app."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from allauth.account.utils import has_verified_email

from orders.models import AccessEntitlement


def _verified_or_redirect(request):
    if not has_verified_email(request.user):
        messages.warning(request, "Please verify your email before continuing.")
        return redirect("account_email")
    return None


def _dashboard_url_with_tab(tab_name):
    base_url = reverse("account_dashboard")
    return f"{base_url}?tab={tab_name}"


@login_required
def dashboard(request):
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    entitlements = (
        AccessEntitlement.objects.filter(user=request.user)
        .select_related("product")
        .order_by("-granted_at")
    )

    unlocked_products = [
        {"product": e.product, "purchase_date": e.granted_at} for e in entitlements
    ]

    requested_tab = (request.GET.get("tab") or "").strip().lower()
    tab_map = {
        "profile": "profile",
        "archive": "archive",
        "my-archive": "archive",
        "my_archive": "archive",
        "delete": "delete",
    }
    active_tab = tab_map.get(requested_tab, "profile")

    context = {
        "unlocked_products": unlocked_products,
        "active_tab": active_tab,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def my_archive(request):
    redirect_response = _verified_or_redirect(request)
    if redirect_response:
        return redirect_response

    # If your project uses dashboard tabs as the single source of truth,
    # keep this route as a redirect.
    return redirect(_dashboard_url_with_tab("my-archive"))


@login_required
def profile(request):
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
            messages.error(request, "Superuser accounts cannot be deleted from the site.")
            return redirect("account_dashboard")

        request.user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home")

    return render(request, "accounts/delete_account.html")
