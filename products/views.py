"""Views for the products app."""

from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Product
from orders.models import AccessEntitlement


class ProductListView(ListView):
    """Public archive catalog with pagination."""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by("-created_at")
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(tagline__icontains=search_query)
                | Q(category__name__icontains=search_query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class ProductDetailView(DetailView):
    """Archive preview page with purchase call to action."""

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        purchased = False
        if self.request.user.is_authenticated:
            purchased = AccessEntitlement.objects.filter(
                user=self.request.user, product=product
            ).exists()

        cart_product_ids = set(self.request.session.get("cart", {}).keys())
        context["in_cart"] = str(product.id) in cart_product_ids
        context["purchased"] = purchased

        return context
