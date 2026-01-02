from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Manage products in admin panel."""

    list_display = (
        "title",
        "category",
        "price",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "category", "created_at")
    search_fields = ("title", "slug", "tagline", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("is_active", "is_featured")
    ordering = ("-created_at",)

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
