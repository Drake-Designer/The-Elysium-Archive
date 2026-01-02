"""
Views for accounts app.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm


def register(request):
    """Handle user registration with a custom register form."""
    # Redirect authenticated users to home
    if request.user.is_authenticated:
        messages.info(request, "You are already registered and logged in.")
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Account created successfully. You can now sign in.",
            )
            return redirect("login")

        messages.error(
            request,
            "Registration failed. Please correct the errors below.",
        )
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    """Handle user login with a custom login form."""
    # Redirect authenticated users to home
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}.")

            # Redirect to next parameter or home
            next_url = request.GET.get("next", "home")
            return redirect(next_url)

        messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@require_POST
def user_logout(request):
    """Handle user logout via POST request only."""
    logout(request)
    messages.info(request, "You have been logged out. See you soon.")
    return redirect("home")
