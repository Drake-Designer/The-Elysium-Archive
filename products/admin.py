from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Manage products in admin."""

    list_display = (
        "title",
        "price",
        "is_active",
        "is_featured",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "is_featured", "created_at")
    search_fields = ("title", "slug", "tagline", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)
    list_editable = ("is_active", "is_featured")
