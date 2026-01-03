"""Views for the checkout app."""

from django.shortcuts import render

from accounts.decorators import verified_email_required


@verified_email_required
def checkout_view(request):
    """Render a placeholder checkout page."""
    return render(request, "checkout/checkout.html")
