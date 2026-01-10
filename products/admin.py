"""Admin configuration for products app."""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms

from .admin_utils import admin_display
from .models import Category, DealBanner, Product, sync_products_deal_status


class ProductAdminForm(forms.ModelForm):
    """Custom ModelForm for Product admin to enforce maxlength on image_alt."""

    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "image_alt" in self.fields:
            # Set maxlength attribute so browser blocks typing beyond 150 chars
            self.fields["image_alt"].widget.attrs["maxlength"] = "150"
            # Helpful placeholder
            self.fields["image_alt"].widget.attrs["placeholder"] = "Short descriptive text (60–125 chars recommended)"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model."""

    class Media:
        css = {
            "all": ("css/admin/admin-categories.css",),
        }

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

    fieldsets = (
        ("📂 Category Information", {"fields": ("name", "slug", "description")}),
        ("📊 Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin_display("Name")
    def name_display(self, obj):
        """Display category name with styling."""
        return format_html(
            '<span class="category-name-display">📂 {}</span>',
            obj.name,
        )

    @admin_display("Slug")
    def slug_display(self, obj):
        """Display slug in monospace."""
        return format_html(
            '<code class="category-slug-display">{}</code>',
            obj.slug,
        )

    @admin_display("Products")
    def product_count(self, obj):
        """Display number of products in this category."""
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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    form = ProductAdminForm

    class Media:
        css = {
            "all": ("css/admin/admin-products.css", "css/admin/admin-product-image-alt.css"),
        }
        js = ("js/admin/image-alt-counter.js",)

    list_display = [
        "image_thumbnail",
        "title",
        "category_display",
        "price_display",
        "status_badges",
        "created_at",
    ]

    list_display_links = ["image_thumbnail", "title"]

    list_filter = [
        "is_active",
        "is_featured",
        "is_deal",
        "deal_manual",
        "deal_exclude",
        "category",
        "created_at",
    ]

    search_fields = ["title", "tagline", "description"]

    prepopulated_fields = {"slug": ("title",)}

    date_hierarchy = "created_at"

    autocomplete_fields = ["category"]

    readonly_fields = ["created_at", "updated_at", "is_deal"]

    fieldsets = (
        ("📝 Product Information", {"fields": ("title", "slug", "tagline", "category")}),
        ("💰 Pricing & Status", {"fields": ("price", "is_active", "is_featured")}),
        ("💰 Deal Rules", {"fields": ("is_deal", "deal_manual", "deal_exclude")}),
        ("📄 Content", {"fields": ("description", "content")}),
        ("🖼️ Media", {"fields": ("image", "image_alt")}),
        ("📊 Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = [
        "mark_as_active",
        "mark_as_inactive",
        "mark_as_deal_manual",
        "remove_deal_manual",
        "exclude_from_category_deals",
        "include_in_category_deals",
    ]

    @admin_display("Image")
    def image_thumbnail(self, obj):
        """Display product image thumbnail."""
        if obj.image:
            return format_html(
                '<img src="{}" class="product-thumbnail" alt="{}">',
                obj.image.url,
                obj.image_alt or obj.title,
            )
        return mark_safe('<div class="product-no-image">📦</div>')

    @admin_display("Category")
    def category_display(self, obj):
        """Display category with badge."""
        if obj.category:
            return format_html(
                '<span class="product-category-badge">{}</span>',
                obj.category.name,
            )
        return mark_safe('<span class="product-no-category">No category</span>')

    @admin_display("Price")
    def price_display(self, obj):
        """Display price with styling."""
        return format_html(
            '<span class="product-price-display">€{}</span>',
            obj.price,
        )

    @admin_display("Status")
    def status_badges(self, obj):
        """Display all status badges."""
        badges = []

        if obj.is_active:
            badges.append('<span class="product-status-badge active">✓ Active</span>')
        else:
            badges.append('<span class="product-status-badge inactive">✗ Inactive</span>')

        if obj.is_featured:
            badges.append('<span class="product-status-badge featured">⭐ Featured</span>')

        if obj.is_deal:
            badges.append('<span class="product-status-badge deal">💰 DEAL</span>')

        if obj.deal_manual:
            badges.append('<span class="product-status-badge manual">✋ Manual</span>')

        if obj.deal_exclude:
            badges.append('<span class="product-status-badge excluded">⛔ Excluded</span>')

        return format_html(
            '<div class="product-status-container">{}</div>',
            mark_safe("".join(badges)),
        )

    def mark_as_active(self, request, queryset):
        """Mark products as active."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} product(s) marked as active.")
    mark_as_active.short_description = "✓ Mark as active"

    def mark_as_inactive(self, request, queryset):
        """Mark products as inactive."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} product(s) marked as inactive.")
    mark_as_inactive.short_description = "✗ Mark as inactive"

    def mark_as_deal_manual(self, request, queryset):
        """Force products as deals using manual flag."""
        product_pks = list(queryset.values_list("pk", flat=True))
        updated = queryset.update(deal_manual=True)
        # Recalculate only the affected products
        sync_products_deal_status(product_pks=product_pks)
        self.message_user(request, f"{updated} product(s) forced as deals.")
    mark_as_deal_manual.short_description = "💰 Force deal (manual)"

    def remove_deal_manual(self, request, queryset):
        """Remove manual deal flag from products."""
        product_pks = list(queryset.values_list("pk", flat=True))
        updated = queryset.update(deal_manual=False)
        sync_products_deal_status(product_pks=product_pks)
        self.message_user(request, f"{updated} product(s) removed from manual deals.")
    remove_deal_manual.short_description = "🚫 Remove manual deal"

    def exclude_from_category_deals(self, request, queryset):
        """Exclude products from category deal banners."""
        product_pks = list(queryset.values_list("pk", flat=True))
        updated = queryset.update(deal_exclude=True)
        sync_products_deal_status(product_pks=product_pks)
        self.message_user(request, f"{updated} product(s) excluded from category deals.")
    exclude_from_category_deals.short_description = "⛔ Exclude from category deals"

    def include_in_category_deals(self, request, queryset):
        """Include products in category deal banners."""
        product_pks = list(queryset.values_list("pk", flat=True))
        updated = queryset.update(deal_exclude=False)
        sync_products_deal_status(product_pks=product_pks)
        self.message_user(request, f"{updated} product(s) included in category deals.")
    include_in_category_deals.short_description = "✅ Include in category deals"


@admin.register(DealBanner)
class DealBannerAdmin(admin.ModelAdmin):
    """Admin interface for DealBanner model with enhanced display."""

    class Media:
        css = {
            "all": ("css/admin/admin-deal-banners.css",),
        }

    list_display = [
        "order",
        "icon_display",
        "title",
        "message_preview",
        "destination_display",
        "category_badge",
        "status_badge",
        "created_at",
    ]

    list_display_links = ["title", "message_preview"]

    list_filter = [
        "is_active",
        "category",
        "created_at",
    ]

    search_fields = ["title", "message", "url"]

    list_editable = ["order"]

    autocomplete_fields = ["product", "category"]

    readonly_fields = ["created_at", "preview_banner"]

    date_hierarchy = "created_at"

    ordering = ["order", "-created_at"]

    fieldsets = (
        ("📝 Banner Content", {
            "fields": ("title", "message", "icon"),
            "description": "Main text and icon displayed in the banner",
        }),
        ("🔗 Link Settings", {
    "fields": ("product", "category", "url"),
    "description": mark_safe(
        '<div class="deal-banner-fieldset-description">'
        "<strong>Link Priority Order:</strong><br>"
        "1. <strong>Product</strong> → Links directly to the selected product page<br>"
        "2. <strong>URL</strong> → Uses the custom URL provided<br>"
        "3. <strong>Category</strong> → Links to archive filtered by category + deals<br>"
        "4. <strong>None</strong> → Links to archive with deals filter only"
        "</div>"
    ),
}),
        ("🎨 Display Options", {
            "fields": ("is_active", "order"),
            "description": "Category also adds a badge to the banner. Lower order number = displayed first.",
        }),
        ("📊 Metadata", {
            "fields": ("created_at", "preview_banner"),
            "classes": ("collapse",),
        }),
    )

    actions = ["activate_banners", "deactivate_banners", "duplicate_banner"]

    @admin_display("🎨")
    def icon_display(self, obj):
        """Display icon with larger size."""
        return format_html(
            '<span class="deal-banner-icon">{}</span>',
            obj.icon,
        )

    @admin_display("Message")
    def message_preview(self, obj):
        """Display truncated message with full text on hover."""
        if len(obj.message) > 50:
            truncated = obj.message[:50] + "..."
            return format_html(
                '<span class="deal-banner-message-preview" title="{}">{}</span>',
                obj.message,
                truncated,
            )
        return obj.message

    @admin_display("Destination")
    def destination_display(self, obj):
        """Display where the banner links to."""
        url = obj.get_url()

        if obj.product:
            icon = "📦"
            label = f"Product: {obj.product.title[:30]}"
            css_class = "type-product"
        elif obj.url:
            icon = "🔗"
            label = f"Custom: {obj.url[:30]}"
            css_class = "type-custom"
        elif obj.category:
            icon = "📂"
            label = f"Category: {obj.category.name}"
            css_class = "type-category"
        else:
            icon = "💰"
            label = "All Deals"
            css_class = "type-default"

        return format_html(
            '<div class="deal-banner-destination">'
            '<span class="deal-banner-destination-label {}">{} {}</span>'
            '<span class="deal-banner-destination-url">{}</span>'
            "</div>",
            css_class,
            icon,
            label,
            url,
        )

    @admin_display("Badge")
    def category_badge(self, obj):
        """Display category badge if present."""
        if obj.category:
            return format_html(
                '<span class="deal-banner-category-badge">{}</span>',
                obj.category.name,
            )
        return mark_safe('<span class="deal-banner-no-badge">No badge</span>')

    @admin_display("Status")
    def status_badge(self, obj):
        """Display active or inactive status."""
        if obj.is_active:
            return mark_safe('<span class="deal-banner-status-badge active">✓ ACTIVE</span>')
        return mark_safe('<span class="deal-banner-status-badge inactive">✗ INACTIVE</span>')

    @admin_display("Banner Preview")
    def preview_banner(self, obj):
        """Display a preview of how the banner will look."""
        if not obj.pk:
            return "Save the banner to see preview"

        category_html = ""
        if obj.category:
            category_html = format_html(
                '<span class="deal-banner-preview-category-badge">{}</span>',
                obj.category.name,
            )

        return format_html(
            '<div class="deal-banner-preview-wrapper">'
            '<a href="{}" target="_blank" class="deal-banner-preview-link">'
            '<span class="deal-banner-preview-icon">{}</span>'
            '<span class="deal-banner-preview-text">'
            '<strong class="deal-banner-preview-title">{}</strong> {}'
            "{}"
            "</span>"
            "</a>"
            "</div>"
            '<p class="deal-banner-preview-url">'
            "<strong>Clicks to:</strong> {}"
            "</p>",
            obj.get_url(),
            obj.icon,
            obj.title.upper(),
            obj.message,
            category_html,
            obj.get_url(),
        )

    def activate_banners(self, request, queryset):
        """Bulk activate selected banners."""
        # Collect affected products/categories before the bulk update
        product_pks = list(queryset.filter(product__isnull=False).values_list("product__pk", flat=True))
        category_pks = list(queryset.filter(category__isnull=False).values_list("category__pk", flat=True))
        updated = queryset.update(is_active=True)
        if product_pks or category_pks:
            sync_products_deal_status(product_pks=product_pks, category_pks=category_pks)
        self.message_user(request, f"{updated} banner(s) successfully activated.")
    activate_banners.short_description = "✓ Activate selected banners"

    def deactivate_banners(self, request, queryset):
        """Bulk deactivate selected banners."""
        product_pks = list(queryset.filter(product__isnull=False).values_list("product__pk", flat=True))
        category_pks = list(queryset.filter(category__isnull=False).values_list("category__pk", flat=True))
        updated = queryset.update(is_active=False)
        if product_pks or category_pks:
            sync_products_deal_status(product_pks=product_pks, category_pks=category_pks)
        self.message_user(request, f"{updated} banner(s) successfully deactivated.")
    deactivate_banners.short_description = "✗ Deactivate selected banners"

    def duplicate_banner(self, request, queryset):
        """Duplicate selected banners."""
        count = 0
        for banner in queryset:
            banner.pk = None
            banner.title = f"{banner.title} (Copy)"
            banner.is_active = False
            banner.save()
            count += 1
        self.message_user(request, f"{count} banner(s) duplicated successfully.")
    duplicate_banner.short_description = "📋 Duplicate selected banners"
