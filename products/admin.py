"""Admin configuration for products app."""

from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from orders.models import AccessEntitlement

from .admin_utils import admin_display
from .models import Category, DealBanner, Product

# ============================
# Product Admin Form
# ============================


class ProductAdminForm(forms.ModelForm):
    """ModelForm for Product admin to enforce maxlength on image_alt."""

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "image_alt" in self.fields:
            self.fields["image_alt"].widget.attrs["maxlength"] = "150"
            self.fields["image_alt"].widget.attrs[
                "placeholder"
            ] = "Short descriptive text (60-125 chars recommended)"


# ============================
# Category Admin
# ============================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""

    class Media:
        css = {"all": ("css/admin/admin-categories.css",)}

    list_display = [
        "name_display",
        "slug_display",
        "product_count",
        "created_at",
    ]
    list_display_links = ["name_display"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "📂 Category Information",
            {"fields": ("name", "slug", "description")},
        ),
        (
            "📊 Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin_display("Name")
    def name_display(self, obj):
        """Display category name."""
        return format_html(
            '<span class="category-name-display">📂 {}</span>',
            obj.name,
        )

    @admin_display("Slug")
    def slug_display(self, obj):
        """Display slug."""
        return format_html(
            '<code class="category-slug-display">{}</code>',
            obj.slug,
        )

    @admin_display("Products")
    def product_count(self, obj):
        """Display number of products."""
        count = obj.products.count()
        css_class = "category-product-count"
        if count == 0:
            css_class += " category-product-count-zero"

        return format_html(
            '<span class="{}">{} product{}</span>',
            css_class,
            count,
            "s" if count != 1 else "",
        )


# ============================
# Product Admin
# ============================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""

    form = ProductAdminForm

    class Media:
        css = {
            "all": (
                "css/admin/admin-products.css",
                "css/admin/admin-product-image-alt.css",
            )
        }
        js = ("js/admin/image-alt-counter.js",)

    list_display = [
        "image_thumbnail",
        "title",
        "category",
        "discount_display",
        "status_badges",
        "created_at",
    ]
    list_display_links = ["image_thumbnail", "title"]

    list_filter = [
        "is_active",
        "is_removed",
        "is_featured",
        "is_deal",
        "category",
    ]

    search_fields = ["title", "tagline", "description"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    autocomplete_fields = ["category"]
    readonly_fields = ["created_at", "updated_at", "is_deal"]

    fieldsets = (
        (
            "📝 Product Information",
            {"fields": ("title", "slug", "tagline", "category")},
        ),
        (
            "💰 Pricing & Status",
            {"fields": ("price", "is_active", "is_removed", "is_featured")},
        ),
        (
            "💰 Deal Status",
            {
                "fields": ("is_deal",),
                "description": (
                    "Deal status is automatically calculated based on "
                    "active deal banners."
                ),
            },
        ),
        ("📄 Content", {"fields": ("description", "content")}),
        ("🖼️ Media", {"fields": ("image", "image_alt")}),
        (
            "📊 Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "publish_products",
        "unpublish_products",
        "mark_as_featured",
        "unmark_as_featured",
        "remove_products_permanently",
    ]

    def has_delete_permission(self, request, obj=None):
        """Allow delete so admin can unpublish via delete."""
        return super().has_delete_permission(request, obj=obj)

    def delete_model(self, request, obj):
        """Convert admin delete into unpublish."""
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])
        self.message_user(
            request,
            "Product removed from catalog (unpublished).",
        )

    def delete_queryset(self, request, queryset):
        """Convert bulk delete into unpublish."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} product(s) removed from catalog (unpublished).",
        )

    def get_actions(self, request):
        """Remove built-in bulk delete action."""
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    @admin_display("Image")
    def image_thumbnail(self, obj):
        """Display product thumbnail."""
        if obj.image:
            return format_html(
                '<img src="{}" class="product-thumbnail" alt="{}">',
                obj.image.url,
                obj.image_alt or obj.title,
            )
        return mark_safe('<div class="product-no-image">📦</div>')

    @admin_display("Discount")
    def discount_display(self, obj):
        """Display discount badge."""
        if obj.is_deal:
            discount = obj.get_discount_percentage()
            if discount > 0:
                return format_html(
                    '<span class="badge bg-danger">-{}%</span>',
                    discount,
                )
        return mark_safe('<span class="text-muted">-</span>')

    @admin_display("Status")
    def status_badges(self, obj):
        """Display status badges."""
        badges = []

        if obj.is_removed:
            badges.append(("removed", "🗑 Removed"))
        elif obj.is_active:
            badges.append(("active", "✓ Active"))
        else:
            badges.append(("inactive", "✗ Unpublished"))

        if obj.is_featured:
            badges.append(("featured", "⭐ Featured"))

        if obj.is_deal:
            badges.append(("deal", "💰 DEAL"))

        badges_html = format_html_join(
            "",
            '<span class="product-status-badge {}">{}</span>',
            badges,
        )

        return format_html(
            '<div class="product-status-container">{}</div>',
            badges_html,
        )

    def publish_products(self, request, queryset):
        """Publish products."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{updated} product(s) published to catalog.",
        )

    def unpublish_products(self, request, queryset):
        """Unpublish products."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} product(s) removed from catalog.",
        )

    def mark_as_featured(self, request, queryset):
        """Mark as featured."""
        count = 0
        for product in queryset:
            if not product.is_featured:
                product.is_featured = True
                product.save(update_fields=["is_featured", "updated_at"])
                count += 1
        self.message_user(
            request,
            f"{count} product(s) marked as featured.",
        )

    def unmark_as_featured(self, request, queryset):
        """Remove featured status."""
        count = 0
        for product in queryset:
            if product.is_featured:
                product.is_featured = False
                product.save(update_fields=["is_featured", "updated_at"])
                count += 1
        self.message_user(
            request,
            f"{count} product(s) unmarked as featured.",
        )

    def remove_products_permanently(self, request, queryset):
        """Remove products or delete if never purchased."""
        product_ids = list(queryset.values_list("id", flat=True))
        if not product_ids:
            self.message_user(request, "No products selected.")
            return

        entitled_ids = set(
            AccessEntitlement.objects.filter(
                product_id__in=product_ids
            ).values_list("product_id", flat=True)
        )

        to_soft_remove = queryset.filter(pk__in=entitled_ids)
        to_hard_delete = queryset.exclude(pk__in=entitled_ids)

        now = timezone.now()
        soft_count = 0
        if to_soft_remove.exists():
            soft_count = to_soft_remove.update(
                is_removed=True,
                is_active=False,
                is_featured=False,
                updated_at=now,
            )

        hard_count = to_hard_delete.count()
        if hard_count:
            to_hard_delete.delete()

        if soft_count and hard_count:
            message = (
                f"{soft_count} removed from public site (buyers kept). "
                f"{hard_count} permanently deleted."
            )
        elif soft_count:
            message = f"{soft_count} removed from public site (buyers kept)."
        elif hard_count:
            message = f"{hard_count} permanently deleted."
        else:
            message = "No products were changed."

        self.message_user(request, message)


# ============================
# Deal Banner Admin
# ============================


@admin.register(DealBanner)
class DealBannerAdmin(admin.ModelAdmin):
    """Admin interface for DealBanner model."""

    class Media:
        css = {"all": ("css/admin/admin-deal-banners.css",)}

    list_display = [
        "order",
        "title",
        "discount_display",
        "destination_display",
        "status_badges",
        "created_at",
    ]
    list_display_links = ["title"]
    list_filter = ["is_active", "is_featured", "category"]
    search_fields = ["title", "message", "url"]
    list_editable = ["order"]
    autocomplete_fields = ["product", "category"]
    readonly_fields = ["created_at", "preview_banner"]
    date_hierarchy = "created_at"
    ordering = ["order", "-created_at"]

    @admin_display("Discount")
    def discount_display(self, obj):
        """Display discount percentage badge."""
        if obj.discount_percentage and obj.discount_percentage > 0:
            discount_value = f"{obj.discount_percentage}".rstrip("0").rstrip(
                "."
            )
            return format_html(
                '<span class="badge bg-danger">-{}%</span>',
                discount_value,
            )
        return mark_safe('<span class="text-muted">-</span>')

    @admin_display("Destination")
    def destination_display(self, obj):
        """Display the banner destination type and URL."""
        if obj.product:
            label = "Product"
            value = obj.product.title
            type_class = "type-product"
        elif obj.category:
            label = "Category"
            value = obj.category.name
            type_class = "type-category"
        elif obj.url:
            label = "Custom URL"
            value = "External link"
            type_class = "type-custom"
        else:
            label = "Deals page"
            value = "Deals archive"
            type_class = "type-default"

        destination_url = obj.get_url()

        return format_html(
            '<div class="deal-banner-destination">'
            '<span class="deal-banner-destination-label {}">{}: {}</span>'
            '<span class="deal-banner-destination-url">{}</span>'
            "</div>",
            type_class,
            label,
            value,
            destination_url,
        )

    @admin_display("Status")
    def status_badges(self, obj):
        """Display active/featured badges."""
        badges = []

        if obj.is_active:
            badges.append(("active", "Active"))
        else:
            badges.append(("inactive", "Inactive"))

        if obj.is_featured:
            badges.append(("featured", "Featured"))

        badges_html = format_html_join(
            "",
            '<span class="deal-banner-status-badge {}">{}</span>',
            badges,
        )

        return format_html(
            '<div class="deal-banner-status-container">{}</div>',
            badges_html,
        )

    @admin_display("Preview")
    def preview_banner(self, obj):
        """Render a read-only banner preview in the admin form."""
        if not obj.pk:
            return mark_safe("Save to preview banner.")

        destination_url = obj.get_url()
        category_badge = ""
        if obj.category:
            category_badge = format_html(
                ' <span class="deal-banner-preview-category-badge">{}</span>',
                obj.category.name,
            )

        return format_html(
            '<div class="deal-banner-preview-wrapper">'
            '<a class="deal-banner-preview-link" href="{}" target="_blank" '
            'rel="noopener noreferrer">'
            '<span class="deal-banner-preview-icon">{}</span>'
            '<span class="deal-banner-preview-text">'
            '<span class="deal-banner-preview-title">{}</span> {}{}'
            "</span>"
            "</a>"
            '<div class="deal-banner-preview-url">{}</div>'
            "</div>",
            destination_url,
            obj.icon,
            obj.title,
            obj.message,
            category_badge,
            destination_url,
        )
