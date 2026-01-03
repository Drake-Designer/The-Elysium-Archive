"""Provide access control helpers for accounts views."""

from functools import wraps

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def verified_email_required(view_func):
    """Ensure the user is authenticated and has a verified email."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in to continue.")
            login_url = f"{reverse('account_login')}?next={request.path}"
            return redirect(login_url)
        if not has_verified_email(request.user):
            messages.warning(
                request,
                "Please verify your email before continuing.",
            )
            return redirect("account_email")
        return view_func(request, *args, **kwargs)

    return _wrapped
