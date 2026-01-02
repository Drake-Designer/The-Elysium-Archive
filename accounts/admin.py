from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile."""

    list_display = ("user", "display_name", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "display_name")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("user", "display_name")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
