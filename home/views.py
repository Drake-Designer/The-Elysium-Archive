"""Views for the home app."""

from django.shortcuts import render
from products.models import Product


def home_view(request):
    """Render the homepage with featured archive entries."""
    featured_products = Product.objects.filter(
        is_active=True, is_featured=True
    ).order_by("created_at")[:6]

    context = {
        "featured_products": featured_products,
    }

    return render(request, "home/index.html", context)


def lore_view(request):
    """Render the lore page."""
    return render(request, "home/lore.html")
