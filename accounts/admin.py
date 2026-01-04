from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.messages import success, error
from django.db.models import Count, Q
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join, mark_safe

from .models import UserProfile


class UserHasPurchasesFilter(admin.SimpleListFilter):
    """Filter users by purchase history."""

    title = "purchases"
    parameter_name = "has_purchases"

    def lookups(self, request, model_admin):
        return (("yes", "Has purchases"), ("no", "No purchases"))

    def queryset(self, request, queryset):
        # Use entitlements since User has reverse FK from orders.AccessEntitlement
        if self.value() == "yes":
            return queryset.filter(entitlements__isnull=False).distinct()
        elif self.value() == "no":
            return queryset.filter(entitlements__isnull=True)
        return queryset


# Unregister the default User admin to use our enhanced version
admin.site.unregister(User)


class UserAdmin(BaseUserAdmin):
    """Enhanced User admin with purchase metrics and quick links."""

    list_display = (
        "username",
        "email",
        "user_status",
        "purchases_count",
        "last_login",
        "date_joined",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        UserHasPurchasesFilter,
    )
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined", "purchases_count")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined"), "classes": ("collapse",)},
        ),
        (
            "Purchase info",
            {"fields": ("purchases_count",), "classes": ("collapse",)},
        ),
    )

    class Media:
        css = {"all": ("css/admin/admin.css",)}

    def get_queryset(self, request):
        """Annotate with purchase count to avoid N+1 queries."""
        queryset = super().get_queryset(request)
        return queryset.annotate(purchase_total=Count("entitlements"))

    def user_status(self, obj):
        """Display user status (active/inactive) with staff/superuser indicators."""
        status_parts = []

        if obj.is_superuser:
            status_parts.append(
                '<span class="badge badge-danger" title="Superuser">👑 Admin</span>'
            )
        elif obj.is_staff:
            status_parts.append(
                '<span class="badge badge-featured" title="Staff">⚙️ Staff</span>'
            )

        if obj.is_active:
            status_parts.append('<span class="badge badge-success">Active</span>')
        else:
            status_parts.append('<span class="badge badge-muted">Inactive</span>')

        return mark_safe(" ".join(status_parts))

    user_status.short_description = "Status"

    def purchases_count(self, obj):
        """Display purchase count as a badge."""
        count = getattr(obj, "purchase_total", 0) or 0
        if count > 0:
            return format_html(
                '<span class="badge badge-gold">{} purchase{}</span>',
                count,
                "s" if count != 1 else "",
            )
        return "-"

    purchases_count.short_description = "Purchases"


# Register our enhanced User admin
admin.site.register(User, UserAdmin)


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

    class Media:
        css = {"all": ("css/admin/admin.css",)}
