"""Views for the checkout app."""

from django.shortcuts import render


def checkout_view(request):
    """Render a placeholder checkout page."""
    return render(request, "checkout/checkout.html")
