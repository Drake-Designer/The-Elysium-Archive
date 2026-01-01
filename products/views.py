"""
Views for the products app
"""

from django.shortcuts import render


def archive_list_view(request):
    """Render the public archive catalog page"""
    return render(request, "products/archive_list.html")
