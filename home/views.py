"""
Views for the home app
"""

from django.shortcuts import render


def home_view(request):
    """Render the homepage"""
    return render(request, "home/index.html")


def lore_view(request):
    """Render the lore page"""
    return render(request, "home/lore.html")
