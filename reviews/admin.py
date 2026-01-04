"""Admin configuration for the reviews app."""

from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for reviews."""

    list_display = ("user", "product", "rating", "created_at")
    list_filter = ("rating", "created_at", "product")
    search_fields = ("user__username", "user__email", "product__title", "body")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Review Information",
            {
                "fields": ("user", "product", "rating", "title"),
            },
        ),
        (
            "Content",
            {
                "fields": ("body",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
