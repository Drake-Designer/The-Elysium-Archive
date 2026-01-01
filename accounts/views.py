"""
Views for accounts app.
"""

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


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
