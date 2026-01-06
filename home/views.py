"""Views for the home app."""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
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


# ==========================================
# ERROR PAGE TESTING (Staff Only)
# ==========================================


@staff_member_required
def test_errors_dashboard(request):
    """Render the error testing dashboard. Staff only."""
    return render(request, "home/test_errors.html")


@staff_member_required
def test_error_400(request):
    """Test 400 Bad Request page. Staff only."""
    raise SuspiciousOperation("Test 400 - Bad Request")


@staff_member_required
def test_error_403(request):
    """Test 403 Forbidden page. Staff only."""
    raise PermissionDenied("Test 403 - Forbidden")


@staff_member_required
def test_error_404(request):
    """Test 404 Not Found page. Staff only."""
    raise Http404("Test 404 - Not Found")


@staff_member_required
def test_error_500(request):
    """Test 500 Server Error page. Staff only."""
    raise Exception("Test 500 - Server Error")
