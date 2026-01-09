"""Views for the products app."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from typing import Any, cast

from .models import Category, Product
from elysium_archive.helpers import user_has_access
from elysium_archive.type_guards import is_authenticated_user
from reviews.forms import ReviewForm


class ProductListView(ListView):
    """Public archive catalog with pagination."""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self) -> QuerySet[Product]:
        """Return active products, optionally filtered by search query and category tag."""
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at")
        )

        search_query = self.request.GET.get("q", "").strip()
        category_slug = self.request.GET.get("cat", "").strip()

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(tagline__icontains=search_query)
                | Q(category__name__icontains=search_query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add search query and category tags to context for template."""
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", "").strip()
        active_category = self.request.GET.get("cat", "").strip()

        categories = (
            Category.objects.filter(products__is_active=True)
            .distinct()
            .order_by("name")
        )

        context["search_query"] = search_query
        context["categories"] = categories
        context["active_category"] = active_category

        return context


class ProductDetailView(DetailView):
    """Archive preview page with purchase call to action."""

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[Product]:
        """Return all products (access control happens in get_object)."""
        return Product.objects.all().select_related("category")

    def get_object(self, queryset: QuerySet[Product] | None = None) -> Product:
        """Return product if accessible, raise 404 otherwise."""
        obj: Product = super().get_object(queryset)

        # Active products are visible to everyone
        if obj.is_active:
            return obj

        # Inactive products: check staff/superuser access
        if is_authenticated_user(self.request.user) and (
            self.request.user.is_staff or self.request.user.is_superuser  # type: ignore[attr-defined]
        ):
            return obj

        # Inactive products: check if user owns it via entitlement
        if is_authenticated_user(self.request.user):
            from orders.models import AccessEntitlement

            if AccessEntitlement.objects.filter(
                user=cast(Any, self.request.user), product=obj
            ).exists():
                return obj

        # No access: raise 404
        raise Http404("Product not found")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add cart, purchase status, and reviews to context."""
        context = super().get_context_data(**kwargs)
        product: Product = self.get_object()

        purchased = user_has_access(self.request.user, product)
        cart_product_ids = set(self.request.session.get("cart", {}).keys())

        reviews = product.reviews.all()
        user_review = None
        can_review = False
        form = None

        if is_authenticated_user(self.request.user) and purchased:
            user_review = product.reviews.filter(user=cast(Any, self.request.user)).first()
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
        if is_authenticated_user(request.user) and request.user.is_superuser:  # type: ignore[attr-defined]
            return super().dispatch(request, *args, **kwargs)

        if is_authenticated_user(request.user):
            from allauth.account.models import EmailAddress
            from django.contrib import messages

            if not EmailAddress.objects.filter(
                user=request.user, verified=True
            ).exists():
                messages.warning(
                    request,
                    "Please verify your email address to access archive content.",
                )
                return redirect("account_email")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset: QuerySet[Product] | None = None) -> Product:
        """Return product and verify user has access."""
        obj: Product = super().get_object(queryset)

        if is_authenticated_user(self.request.user) and self.request.user.is_superuser:  # type: ignore[attr-defined]
            return obj

        if not user_has_access(self.request.user, obj):
            raise PermissionDenied("You must purchase this archive to read it.")

        return obj

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add navigation context for back button."""
        context = super().get_context_data(**kwargs)
        context["from_my_archive"] = self.request.GET.get("from") == "my_archive"
        return context
