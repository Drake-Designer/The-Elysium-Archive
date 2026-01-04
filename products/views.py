"""Views for the products app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Product
from elysium_archive.helpers import user_has_access
from reviews.models import Review
from reviews.forms import ReviewForm


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
        # Include all products; get_object() will enforce access control.
        return Product.objects.all()

    def get_object(self, queryset=None):
        # Allow staff/superusers to see inactive products.
        # Allow owners to see their purchased inactive products.
        obj = super().get_object(queryset)

        if obj.is_active:
            return obj

        # If product is inactive, check if user is staff or owner.
        if self.request.user.is_staff or self.request.user.is_superuser:
            return obj

        if self.request.user.is_authenticated:
            # Check if user owns this product via AccessEntitlement.
            from orders.models import AccessEntitlement

            if AccessEntitlement.objects.filter(
                user=self.request.user, product=obj
            ).exists():
                return obj

        # User is not authorized to view this inactive product.
        from django.http import Http404

        raise Http404("Product not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        purchased = user_has_access(self.request.user, product)
        cart_product_ids = set(self.request.session.get("cart", {}).keys())

        # Reviews are visible to everyone, but only buyers can submit.
        reviews = product.reviews.all()
        user_review = None
        can_review = False
        form = None

        if self.request.user.is_authenticated and purchased:
            user_review = product.reviews.filter(user=self.request.user).first()
            can_review = not user_review
            if can_review:
                form = ReviewForm()

        context["in_cart"] = str(product.id) in cart_product_ids
        context["purchased"] = purchased
        context["reviews"] = reviews
        context["user_review"] = user_review
        context["can_review"] = can_review
        context["form"] = form

        return context


class ArchiveReadView(LoginRequiredMixin, DetailView):
    """Private reading page for purchased archive entries."""

    model = Product
    template_name = "products/archive_read.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    login_url = "/accounts/login/"

    def dispatch(self, request, *args, **kwargs):
        """Check email verification before processing request."""
        # Check if user email is verified
        if request.user.is_authenticated:
            from allauth.account.models import EmailAddress

            if not EmailAddress.objects.filter(
                user=request.user, verified=True
            ).exists():
                from django.shortcuts import redirect
                from django.contrib import messages

                messages.warning(
                    request,
                    "Please verify your email address to access archive content.",
                )
                return redirect("account_email")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """Return product and verify user has access."""
        obj = super().get_object(queryset)

        # Verify user has purchased this product
        if not user_has_access(self.request.user, obj):
            raise PermissionDenied("You must purchase this archive to read it.")

        return obj

    def get_context_data(self, **kwargs):
        """Add navigation context."""
        context = super().get_context_data(**kwargs)
        context["from_my_archive"] = self.request.GET.get("from") == "my_archive"
        return context
