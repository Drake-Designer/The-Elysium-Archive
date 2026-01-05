from django import forms
from django.contrib import admin
from django.contrib.messages import error, success
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Category, Product


# Custom filters for Products.


class HasPurchasesFilter(admin.SimpleListFilter):
    """Filter products by entitlement count (purchases)."""

    title = "purchases"
    parameter_name = "has_purchases"

    def lookups(self, request, model_admin):
        """Return filter options."""
        return (
            ("yes", "Has purchases"),
            ("no", "No purchases"),
        )

    def queryset(self, request, queryset):
        """Filter queryset based on entitlements count."""
        if self.value() == "yes":
            return queryset.filter(entitlements__isnull=False).distinct()
        elif self.value() == "no":
            return queryset.filter(entitlements__isnull=True)
        return queryset


class HasImageFilter(admin.SimpleListFilter):
    """Filter products by image presence."""

    title = "image"
    parameter_name = "has_image"

    def lookups(self, request, model_admin):
        """Return filter options."""
        return (
            ("yes", "Has image"),
            ("no", "No image"),
        )

    def queryset(self, request, queryset):
        """Filter queryset based on image field."""
        if self.value() == "yes":
            return queryset.exclude(image="")
        elif self.value() == "no":
            return queryset.filter(image="")
        return queryset


class ProductAdminForm(forms.ModelForm):
    """Use CKEditor only for Product.content in admin."""

    content = forms.CharField(
        required=False,
        widget=CKEditorUploadingWidget(config_name="product_content"),
    )

    class Meta:
        model = Product
        fields = "__all__"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Manage archive categories."""

    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Manage products in admin panel with powerful tools."""

    form = ProductAdminForm

    list_display = (
        "title",
        "entitlement_count",
        "status_badge",
        "featured_toggle",
        "has_image_badge",
        "category",
        "price",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_featured",
        "category",
        "created_at",
        HasPurchasesFilter,
        HasImageFilter,
    )
    search_fields = ("title", "slug", "tagline", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_editable = ()
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("category",)
    actions = [
        "safe_delete_products",
        "mark_as_featured",
        "remove_featured",
    ]

    fieldsets = (
        ("Archive Details", {"fields": ("title", "slug", "tagline", "category")}),
        ("Content", {"fields": ("description", "content"), "classes": ("collapse",)}),
        ("Media", {"fields": ("image", "image_alt")}),
        ("Status", {"fields": ("price", "is_active", "is_featured")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    class Media:
        css = {"all": ("css/admin/admin.css",)}

    def get_urls(self):
        """Add custom URL for featured toggle."""
        custom_urls = [
            path(
                "<int:product_id>/toggle-featured/",
                self.admin_site.admin_view(self.toggle_featured_view),
                name="products_product_toggle_featured",
            ),
        ]
        return custom_urls + super().get_urls()

    @require_http_methods(["POST"])
    def toggle_featured_view(self, request, product_id):
        """Toggle is_featured for a product and redirect back."""
        product = get_object_or_404(Product, pk=product_id)

        # Verify permission to change
        if not self.has_change_permission(request, product):
            raise Http404("Permission denied")

        # Toggle featured status
        product.is_featured = not product.is_featured
        product.save(update_fields=["is_featured"])

        # Show success message
        state = "featured" if product.is_featured else "not featured"
        success(request, f'"{product.title}" is now {state}.')

        # Redirect back to list or referer
        referer = request.META.get("HTTP_REFERER")
        return HttpResponseRedirect(referer or self.get_changelist_url(request))

    def get_changelist_url(self, request):
        """Get admin change list URL."""
        return reverse("admin:products_product_changelist")

    def get_queryset(self, request):
        """Annotate queryset with entitlement count to avoid N+1 queries."""
        queryset = super().get_queryset(request)
        return queryset.annotate(entitlement_total=Count("entitlements"))

    def entitlement_count(self, obj):
        """Display number of entitlements (purchases) as badge."""
        count = getattr(obj, "entitlement_total", 0) or 0
        if count > 0:
            return format_html(
                '<span class="badge badge-gold">{} purchase{}</span>',
                count,
                "s" if count != 1 else "",
            )
        return "-"

    entitlement_count.short_description = "Purchases"

    def status_badge(self, obj):
        """Display active/archived status as a badge."""
        if obj.is_active:
            return mark_safe('<span class="badge badge-success">Active</span>')
        else:
            return mark_safe('<span class="badge badge-muted">Archived</span>')

    status_badge.short_description = "Status"

    def featured_toggle(self, obj):
        """Display featured status with toggle link."""
        if obj.is_featured:
            badge = '<span class="badge badge-featured">⭐ Featured</span>'
        else:
            badge = '<span class="badge badge-not-featured">Not featured</span>'

        # Generate POST form for toggle (CSRF safe via Django admin middleware)
        toggle_url = reverse(
            "admin:products_product_toggle_featured",
            args=[obj.pk],
        )
        # Django admin handles CSRF automatically when using admin_site.admin_view()
        form_html = (
            f'<form method="post" action="{toggle_url}" style="display:inline;">'
            f'<button type="submit" class="admin-btn-toggle" title="Click to toggle featured status">'
            f"{badge}</button></form>"
        )
        return mark_safe(form_html)

    featured_toggle.short_description = "Featured"

    def has_image_badge(self, obj):
        """Display image presence as badge."""
        if obj.image:
            return mark_safe('<span class="badge badge-image">📷 Has image</span>')
        else:
            return mark_safe('<span class="badge badge-no-image">No image</span>')

    has_image_badge.short_description = "Image"

    def mark_as_featured(self, request, queryset):
        """Bulk action to mark products as featured."""
        updated = queryset.update(is_featured=True)
        success(request, f"Marked {updated} product(s) as featured.")

    mark_as_featured.short_description = "Mark selected as featured"

    def remove_featured(self, request, queryset):
        """Bulk action to remove featured status."""
        updated = queryset.update(is_featured=False)
        success(request, f"Removed featured status from {updated} product(s).")

    remove_featured.short_description = "Remove featured status"

    def get_actions(self, request):
        """Remove default delete_selected action; keep only safe_delete_products."""
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        """Allow deletion attempts; actual deletion is gated in delete_model/delete_queryset."""
        return True

    def _get_protected_titles(self, queryset):
        """Get titles of products with entitlements in single query."""
        protected_titles = (
            queryset.filter(entitlements__isnull=False)
            .distinct()
            .values_list("title", flat=True)
        )
        return list(protected_titles)

    def delete_model(self, request, obj):
        """Block deletion if product has entitlements; suggest soft delete instead."""
        if obj.entitlements.exists():
            count = obj.entitlements.count()
            error(
                request,
                format_html(
                    "Cannot delete <strong>{}</strong>: {} user{} {} purchased this. Use soft delete (set inactive) instead.",
                    obj.title,
                    count,
                    "s" if count != 1 else "",
                    "have" if count != 1 else "has",
                ),
            )
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Block bulk deletion if any product has entitlements (fallback protection)."""
        protected_titles = self._get_protected_titles(queryset)

        if protected_titles:
            titles_html = format_html_join(
                ", ",
                "<strong>{}</strong>",
                ((title,) for title in protected_titles),
            )
            error(
                request,
                format_html(
                    "Cannot delete: {} {} purchased. Use soft delete (set inactive) instead.",
                    titles_html,
                    "have been" if len(protected_titles) > 1 else "has been",
                ),
            )
            return

        super().delete_queryset(request, queryset)

    def safe_delete_products(self, request, queryset):
        """Custom bulk delete action with entitlement protection (ALL-OR-NOTHING)."""
        protected_titles = self._get_protected_titles(queryset)

        if protected_titles:
            titles_html = format_html_join(
                ", ",
                "<strong>{}</strong>",
                ((title,) for title in protected_titles),
            )
            error(
                request,
                format_html(
                    "Delete blocked: {} {} purchased. "
                    "Consider soft delete (set <strong>is_active=False</strong>) instead.",
                    titles_html,
                    "have been" if len(protected_titles) > 1 else "has been",
                ),
            )
            return

        count = queryset.count()
        super().delete_queryset(request, queryset)
        success(
            request,
            format_html(
                "Successfully deleted <strong>{}</strong> product{}.",
                count,
                "s" if count != 1 else "",
            ),
        )

    safe_delete_products.short_description = "Delete selected (protected)"
