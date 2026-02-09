"""Views for the products app."""

from __future__ import annotations

from typing import Any, cast

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from elysium_archive.helpers import user_has_access
from elysium_archive.type_guards import is_authenticated_user
from reviews.forms import ReviewForm

from .models import Category, Product


class ProductListView(ListView):
    """Show a public archive catalog with pagination."""

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self) -> QuerySet[Product]:
        """Return active products, optionally filtered by search, category, or.

        deals.
        """
        queryset = (
            Product.objects.filter(is_active=True, is_removed=False)
            .select_related("category")
            .order_by("-created_at")
        )

        search_query = self.request.GET.get("q", "").strip()
        category_slug = self.request.GET.get("cat", "").strip()
        show_deals = (
            self.request.GET.get("deals", "").strip().lower() == "true"
        )

        if show_deals:
            queryset = queryset.filter(is_deal=True)

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
        """Add search query, category tags, and deals filter to context."""
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", "").strip()
        active_category = self.request.GET.get("cat", "").strip()
        show_deals = (
            self.request.GET.get("deals", "").strip().lower() == "true"
        )

        categories = (
            Category.objects.filter(
                products__is_active=True, products__is_removed=False
            )
            .distinct()
            .order_by("name")
        )

        context["search_query"] = search_query
        context["categories"] = categories
        context["active_category"] = active_category
        context["show_deals"] = show_deals

        return context


class ProductDetailView(DetailView):
    """Show an archive preview page with purchase call to action."""

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self) -> QuerySet[Product]:
        """Return all products and prefetch related data for the detail.

        view.
        """
        return (
            Product.objects.all()
            .select_related("category")
            .prefetch_related("reviews", "reviews__user")
        )

    def get_object(self, queryset: QuerySet[Product] | None = None) -> Product:
        """Return a product if it is accessible, raise 404 otherwise."""
        obj = cast(Product, super().get_object(queryset))

        if obj.is_removed:
            if is_authenticated_user(self.request.user) and (
                getattr(self.request.user, "is_staff", False)
                or getattr(self.request.user, "is_superuser", False)
            ):
                return obj
            raise Http404("Product not found")

        if obj.is_active:
            return obj

        if is_authenticated_user(self.request.user) and (
            getattr(self.request.user, "is_staff", False)
            or getattr(self.request.user, "is_superuser", False)
        ):
            return obj

        if is_authenticated_user(self.request.user):
            from orders.models import AccessEntitlement

            if AccessEntitlement.objects.filter(
                user=cast(Any, self.request.user),
                product=obj,
            ).exists():
                return obj

        raise Http404("Product not found")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add cart, purchase status, and reviews to context."""
        context = super().get_context_data(**kwargs)
        product = cast(Product, context["product"])

        purchased = user_has_access(self.request.user, product)
        cart_product_ids = set(self.request.session.get("cart", {}).keys())

        reviews = []
        user_review = None
        can_review = False
        form = None

        if not product.is_removed:
            reviews = product.reviews.all()  # type: ignore[attr-defined]

            if is_authenticated_user(self.request.user) and purchased:
                user_review = product.reviews.filter(
                    user=cast(Any, self.request.user)
                ).first()  # type: ignore[attr-defined]
                can_review = not user_review
                if can_review:
                    form = ReviewForm()

        context["in_cart"] = str(product.pk) in cart_product_ids
        context["purchased"] = purchased
        context["reviews"] = reviews
        context["user_review"] = user_review
        context["can_review"] = can_review
        context["form"] = form

        return context


class ArchiveReadView(LoginRequiredMixin, DetailView):
    """Show a private reading page for purchased archive entries."""

    model = Product
    template_name = "products/archive_read.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def dispatch(self, request, *args, **kwargs):
        """Check email verification before processing the request."""
        if is_authenticated_user(request.user) and getattr(
            request.user, "is_superuser", False
        ):
            return super().dispatch(request, *args, **kwargs)

        if is_authenticated_user(request.user) and not has_verified_email(
            request.user
        ):
            messages.warning(
                request,
                "Please verify your email address to access archive content.",
            )
            return redirect("account_email")

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset: QuerySet[Product] | None = None) -> Product:
        """Return product and verify user has access."""
        obj = cast(Product, super().get_object(queryset))

        if is_authenticated_user(self.request.user) and getattr(
            self.request.user, "is_superuser", False
        ):
            return obj

        if not user_has_access(self.request.user, obj):
            raise PermissionDenied(
                "You must purchase this archive to read it."
            )

        return obj

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add navigation context for back button."""
        context = super().get_context_data(**kwargs)
        context["from_my_archive"] = (
            self.request.GET.get("from") == "my_archive"
        )
        return context
