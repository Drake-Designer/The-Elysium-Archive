"""Views for the home app."""
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from products.models import Product, DealBanner


def home_view(request):
    """
    Render the homepage with featured archive entries and dynamic sections.
    
    Displays:
    - Custom deal banners (admin-managed promotional carousel)
    - Featured archive entries (up to 6)
    - Latest archive entries (up to 3)
    """
    # Featured products for carousel
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category').order_by('-created_at')[:6]
    
    # Latest products for quick preview
    latest_products = Product.objects.filter(
        is_active=True
    ).select_related('category').order_by('-created_at')[:3]
    
    # Active deal banners for scrolling promotional carousel
    deal_banners = DealBanner.objects.filter(
        is_active=True
    ).select_related('product', 'category').order_by('order', '-created_at')[:10]
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'deal_banners': deal_banners,
    }
    
    return render(request, 'home/index.html', context)


def lore_view(request):
    """Render the lore page with world-building content."""
    return render(request, 'home/lore.html')


# ==========================================
# ERROR PAGE TESTING (Staff Only)
# ==========================================

@staff_member_required
def test_errors_dashboard(request):
    """Render the error testing dashboard. Staff only."""
    return render(request, 'home/test_errors.html')


@staff_member_required
def test_error_400(request):
    """Test 400 Bad Request page. Staff only."""
    raise SuspiciousOperation('Test 400 - Bad Request')


@staff_member_required
def test_error_403(request):
    """Test 403 Forbidden page. Staff only."""
    raise PermissionDenied('Test 403 - Forbidden')


@staff_member_required
def test_error_404(request):
    """Test 404 Not Found page. Staff only."""
    raise Http404('Test 404 - Not Found')


@staff_member_required
def test_error_500(request):
    """Test 500 Server Error page. Staff only."""
    raise Exception('Test 500 - Server Error')
