"""Admin configuration for products app."""
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe


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
            # Set maxlength so the browser blocks typing beyond 150 chars
            self.fields["image_alt"].widget.attrs["maxlength"] = "150"
            # Add a helpful placeholder for the admin form
            self.fields["image_alt"].widget.attrs["placeholder"] = (
                "Short descriptive text (60–125 chars recommended)"
            )



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
    date_hierarchy = "created_at"

    fieldsets = (
        ("📂 Category Information", {"fields": ("name", "slug", "description")}),
        (
            "📊 Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
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
            "all": (
                "css/admin/admin-products.css",
                "css/admin/admin-product-image-alt.css",
            ),
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
        ("💰 Pricing & Status", {"fields": ("price", "is_active", "is_featured")}),
        (
            "💰 Deal Status",
            {
                "fields": ("is_deal",),
                "description": "Deal status is automatically calculated based on active deal banners.",
            },
        ),
        ("📄 Content", {"fields": ("description", "content")}),
        ("🖼️ Media", {"fields": ("image", "image_alt")}),
        (
            "📊 Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    actions = [
        "publish_products",
        "unpublish_products",
        "mark_as_featured",
        "unmark_as_featured",
    ]

    def has_delete_permission(self, request, obj=None):
        """Allow the delete view so admin can unpublish through delete."""
        return super().has_delete_permission(request, obj=obj)

    def delete_model(self, request, obj):
        """Convert admin delete into unpublish."""
        obj.is_active = False
        obj.save(update_fields=["is_active", "updated_at"])
        self.message_user(request, "Product removed from catalog (unpublished).")

    def delete_queryset(self, request, queryset):
        """Convert bulk admin delete into unpublish."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated} product(s) removed from catalog (unpublished)."
        )

    def get_actions(self, request):
        """Remove built-in bulk delete action."""
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

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

    @admin_display("Discount")
    def discount_display(self, obj):
        """Display discount percentage if product is a deal."""
        if obj.is_deal:
            discount = obj.get_discount_percentage()
            if discount > 0:
                return format_html(
                    '<span class="badge bg-danger">-{}%</span>',
                    discount,
                )
        return mark_safe('<span class="text-muted">—</span>')

    @admin_display("Status")
    def status_badges(self, obj):
        """Display all status badges."""
        badges = []

        if obj.is_active:
            badges.append('<span class="product-status-badge active">✓ Active</span>')
        else:
            badges.append(
                '<span class="product-status-badge inactive">✗ Unpublished</span>'
            )

        if obj.is_featured:
            badges.append(
                '<span class="product-status-badge featured">⭐ Featured</span>'
            )

        if obj.is_deal:
            badges.append('<span class="product-status-badge deal">💰 DEAL</span>')

        return format_html(
            '<div class="product-status-container">{}</div>',
            mark_safe("".join(badges)),
        )

    def publish_products(self, request, queryset):
        """Publish products to the public catalog."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} product(s) published to catalog.")

    publish_products.short_description = "✅ Publish selected products"

    def unpublish_products(self, request, queryset):
        """Unpublish products from the public catalog."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} product(s) removed from catalog.")

    unpublish_products.short_description = "🚫 Remove from catalog (unpublish)"

    def mark_as_featured(self, request, queryset):
        """Mark products as featured and sync with banners."""
        count = 0
        for product in queryset:
            if not product.is_featured:
                product.is_featured = True
                product.save(update_fields=["is_featured", "updated_at"])
                count += 1
        self.message_user(request, f"{count} product(s) marked as featured.")

    mark_as_featured.short_description = "⭐ Mark as featured"

    def unmark_as_featured(self, request, queryset):
        """Remove featured status from products and sync with banners."""
        count = 0
        for product in queryset:
            if product.is_featured:
                product.is_featured = False
                product.save(update_fields=["is_featured", "updated_at"])
                count += 1
        self.message_user(request, f"{count} product(s) unmarked as featured.")

    unmark_as_featured.short_description = "⭐ Remove featured status"



@admin.register(DealBanner)
class DealBannerAdmin(admin.ModelAdmin):
    """Admin interface for DealBanner model with enhanced display."""

    class Media:
        css = {
            "all": ("css/admin/admin-deal-banners.css",),
        }

    list_display = [
        "order",
        "title",
        "discount_display",
        "destination_display",
        "status_badges",
        "created_at",
    ]

    list_display_links = ["title"]

    list_filter = [
        "is_active",
        "is_featured",
        "category",
    ]

    search_fields = ["title", "message", "url"]
    list_editable = ["order"]
    autocomplete_fields = ["product", "category"]
    readonly_fields = ["created_at", "preview_banner"]
    date_hierarchy = "created_at"
    ordering = ["order", "-created_at"]

    fieldsets = (
        (
            "📝 Banner Content",
            {
                "fields": ("title", "message", "icon"),
                "description": "Main text and icon displayed in the banner",
            },
        ),
        (
            "💰 Discount Settings",
            {
                "fields": ("discount_percentage",),
                "description": "Discount applied to linked product or all products in linked category",
            },
        ),
        (
            "🔗 Link Settings",
            {
                "fields": ("product", "category", "url"),
                "description": mark_safe(
                    '<div class="deal-banner-fieldset-description">'
                    "<strong>⚠️ Exclusivity Rules:</strong><br>"
                    "• Only products and categories WITHOUT existing active banners are shown<br>"
                    "• Products in categories with active banners are automatically hidden<br>"
                    "• Categories with products that have active banners are automatically hidden<br><br>"
                    "<strong>Link Priority Order:</strong><br>"
                    "1. <strong>Product</strong> → Links directly to the selected product page<br>"
                    "2. <strong>URL</strong> → Uses the custom URL provided<br>"
                    "3. <strong>Category</strong> → Links to archive filtered by category + deals<br>"
                    "4. <strong>None</strong> → Links to archive with deals filter only"
                    "</div>"
                ),
            },
        ),
        (
            "🎨 Display Options",
            {
                "fields": ("is_active", "is_featured", "order"),
                "description": "Featured banners appear first. Lower order number = displayed first.",
            },
        ),
        (
            "📊 Metadata",
            {
                "fields": ("created_at", "preview_banner"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "activate_banners",
        "deactivate_banners",
        "mark_as_featured",
        "unmark_as_featured",
        "duplicate_banner",
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter available products and categories to prevent conflicts."""

        if db_field.name == "product":
            # Exclude products that already have an active banner
            products_with_banners = list(
                DealBanner.objects.filter(
                    is_active=True, product__isnull=False
                ).values_list("product_id", flat=True)
            )

            # Exclude products whose category has an active banner
            categories_with_banners = list(
                DealBanner.objects.filter(
                    is_active=True, category__isnull=False
                ).values_list("category_id", flat=True)
            )

            # If editing existing banner, allow current product
            try:
                resolver_match = getattr(request, "resolver_match", None)
                if resolver_match:
                    object_id = resolver_match.kwargs.get("object_id")
                    if object_id:
                        current_banner = DealBanner.objects.get(pk=object_id)
                        if (
                            hasattr(current_banner, "product")
                            and current_banner.product
                        ):
                            current_product_id = current_banner.product.pk
                            products_with_banners = [
                                pid
                                for pid in products_with_banners
                                if pid != current_product_id
                            ]
            except (DealBanner.DoesNotExist, AttributeError, KeyError):
                pass

            kwargs["queryset"] = (
                Product.objects.filter(is_active=True)
                .exclude(pk__in=products_with_banners)
                .exclude(category_id__in=categories_with_banners)
            )

        if db_field.name == "category":
            # Exclude categories that already have an active banner
            categories_with_banners = list(
                DealBanner.objects.filter(
                    is_active=True, category__isnull=False
                ).values_list("category_id", flat=True)
            )

            # Exclude categories that have products with active banners
            categories_with_product_banners = list(
                Product.objects.filter(dealbanner__is_active=True)
                .values_list("category_id", flat=True)
                .distinct()
            )

            # If editing existing banner, allow current category
            try:
                resolver_match = getattr(request, "resolver_match", None)
                if resolver_match:
                    object_id = resolver_match.kwargs.get("object_id")
                    if object_id:
                        current_banner = DealBanner.objects.get(pk=object_id)
                        if (
                            hasattr(current_banner, "category")
                            and current_banner.category
                        ):
                            current_category_id = current_banner.category.pk
                            categories_with_banners = [
                                cid
                                for cid in categories_with_banners
                                if cid != current_category_id
                            ]
                            categories_with_product_banners = [
                                cid
                                for cid in categories_with_product_banners
                                if cid != current_category_id
                            ]
            except (DealBanner.DoesNotExist, AttributeError, KeyError):
                pass

            kwargs["queryset"] = Category.objects.exclude(
                pk__in=list(
                    set(categories_with_banners + categories_with_product_banners)
                )
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin_display("Discount")
    def discount_display(self, obj):
        """Display discount percentage."""
        if obj.discount_percentage > 0:
            return format_html(
                '<span class="badge bg-danger">-{}%</span>',
                int(obj.discount_percentage),
            )
        return mark_safe('<span class="text-muted">No discount</span>')

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
            '<div class="deal-banner-destination {}">'
            '<span class="deal-banner-destination-label">{} {}</span>'
            '<span class="deal-banner-destination-url">{}</span>'
            "</div>",
            css_class,
            icon,
            label,
            url,
        )

    @admin_display("Status")
    def status_badges(self, obj):
        """Display active and featured status."""
        badges = []

        if obj.is_active:
            badges.append(
                '<span class="deal-banner-status-badge active">✓ ACTIVE</span>'
            )
        else:
            badges.append(
                '<span class="deal-banner-status-badge inactive">✗ INACTIVE</span>'
            )

        if obj.is_featured:
            badges.append(
                '<span class="deal-banner-status-badge featured">⭐ FEATURED</span>'
            )

        return format_html(
            '<div class="deal-banner-status-container">{}</div>',
            mark_safe("".join(badges)),
        )

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

        discount_html = ""
        if obj.discount_percentage > 0:
            discount_html = format_html(
                '<span class="badge bg-danger ms-2">-{}%</span>',
                int(obj.discount_percentage),
            )

        return format_html(
            '<div class="deal-banner-preview-wrapper">'
            '<a href="{}" target="_blank" class="deal-banner-preview-link">'
            '<span class="deal-banner-preview-icon">{}</span>'
            '<span class="deal-banner-preview-text">'
            '<strong class="deal-banner-preview-title">{}</strong> {}'
            "</span>"
            "{}{}"
            "</a>"
            "</div>"
            '<p class="deal-banner-preview-url"><strong>Clicks to:</strong> {}</p>',
            obj.get_url(),
            obj.icon,
            obj.title.upper(),
            obj.message,
            category_html,
            discount_html,
            obj.get_url(),
        )

    def activate_banners(self, request, queryset):
        """Bulk activate selected banners."""
        # Use .save() on each banner to trigger the sync logic
        count = 0
        for banner in queryset:
            if not banner.is_active:
                banner.is_active = True
                banner.save()
                count += 1

        self.message_user(request, f"{count} banner(s) successfully activated.")

    activate_banners.short_description = "✅ Activate selected banners"

    def deactivate_banners(self, request, queryset):
        """Bulk deactivate selected banners."""
        # Use .save() on each banner to trigger the sync logic
        count = 0
        for banner in queryset:
            if banner.is_active:
                banner.is_active = False
                banner.save()
                count += 1

        self.message_user(request, f"{count} banner(s) successfully deactivated.")

    deactivate_banners.short_description = "🚫 Deactivate selected banners"

    def mark_as_featured(self, request, queryset):
        """Mark banners as featured."""
        # Use .save() on each banner to trigger the sync logic
        count = 0
        for banner in queryset:
            if not banner.is_featured:
                banner.is_featured = True
                banner.save()
                count += 1

        self.message_user(request, f"{count} banner(s) marked as featured.")

    mark_as_featured.short_description = "⭐ Mark as featured"

    def unmark_as_featured(self, request, queryset):
        """Remove featured status from banners."""
        # Use .save() on each banner to trigger the sync logic
        count = 0
        for banner in queryset:
            if banner.is_featured:
                banner.is_featured = False
                banner.save()
                count += 1

        self.message_user(request, f"{count} banner(s) unmarked as featured.")

    unmark_as_featured.short_description = "⭐ Remove featured status"

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