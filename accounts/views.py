"""
Views for accounts app.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


def register(request):
    """Handle user registration with Django built-in form."""
    # Redirect authenticated users to home.
    if request.user.is_authenticated:
        messages.info(request, "You are already registered and logged in.")
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your account has been created. You may now enter the Archive.",
            )
            return redirect("login")
        else:
            messages.error(
                request,
                "Registration failed. Please correct the errors below.",
            )
    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    """Handle user login with Django built-in form."""
    # Redirect authenticated users to home.
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}.")
            # Redirect to next parameter or home.
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


@require_POST
def user_logout(request):
    """Handle user logout via POST request only."""
    logout(request)
    messages.success(
        request, "You have been logged out. The Archive awaits your return."
    )
    return redirect("home")
