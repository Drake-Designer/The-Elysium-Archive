"""Admin interface for accounts app."""

import logging

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.html import format_html


User = get_user_model()
logger = logging.getLogger(__name__)


class HasPurchasesFilter(admin.SimpleListFilter):
    """Filter users by purchase history."""

    title = "purchases"
    parameter_name = "has_purchases"

    def lookups(self, request, model_admin):
        """Return filter options."""
        return (
            ("yes", "Has purchases"),
            ("no", "No purchases"),
        )

    def queryset(self, request, queryset):
        """Filter users based on entitlements."""
        if self.value() == "yes":
            return queryset.filter(entitlements__isnull=False).distinct()
        elif self.value() == "no":
            return queryset.filter(entitlements__isnull=True)
        return queryset


class UserAdmin(BaseUserAdmin):
    """Custom user admin with purchase tracking."""

    class Media:
        css = {"all": ("css/admin/admin-accounts.css",)}

    list_display = (
        "user_display",
        "email",
        "email_verified_badge",
        "purchase_count",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_display_links = ("user_display",)

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        HasPurchasesFilter,
    )

    search_fields = ("username", "email", "first_name", "last_name")

    def get_queryset(self, request):
        """Annotate users with entitlement count."""
        queryset = super().get_queryset(request)
        return queryset.annotate(entitlement_total=Count("entitlements"))

    def user_display(self, obj):
        """Display user with avatar/placeholder."""
        try:
            if hasattr(obj, "profile") and obj.profile.profile_picture:
                return format_html(
                    '<div class="user-profile-display">'
                    '<img src="{}" class="user-avatar" alt="{}">'
                    '<div class="user-info">'
                    '<span class="user-display-name">{}</span>'
                    '<span class="user-username">@{}</span>'
                    "</div>"
                    "</div>",
                    obj.profile.profile_picture.url,
                    obj.username,
                    obj.profile.get_display_name(),
                    obj.username,
                )
        except Exception as exc:
            logger.warning(
                "Failed to build user display for user %s.",
                obj.pk,
                exc_info=exc,
            )

        # Fallback: first letter avatar
        initial = obj.username[0].upper() if obj.username else "?"
        return format_html(
            '<div class="user-profile-display">'
            '<div class="user-avatar-placeholder">{}</div>'
            '<div class="user-info">'
            '<span class="user-display-name">{}</span>'
            '<span class="user-username">@{}</span>'
            "</div>"
            "</div>",
            initial,
            obj.get_full_name() or obj.username,
            obj.username,
        )

    user_display.short_description = "User"

    def email_verified_badge(self, obj):
        """Display email verification status as badge."""
        try:
            from allauth.account.models import EmailAddress

            verified = EmailAddress.objects.filter(
                user=obj, verified=True
            ).exists()
        except Exception as exc:
            verified = False
            logger.warning(
                "Failed to check email verification for user %s.",
                obj.pk,
                exc_info=exc,
            )

        if verified:
            return format_html(
                '<span class="badge-success">{}</span>',
                "✓ Verified",
            )
        return format_html(
            '<span class="badge-warning">{}</span>',
            "⚠ Unverified",
        )

    email_verified_badge.short_description = "Email"

    def purchase_count(self, obj):
        """Display number of purchases as badge."""
        count = getattr(obj, "entitlement_total", 0) or 0
        if count > 0:
            return format_html(
                '<span class="badge-gold">{} purchase{}</span>',
                count,
                "s" if count != 1 else "",
            )
        return format_html(
            '<span class="badge-muted">{}</span>',
            "No purchases",
        )

    purchase_count.short_description = "Purchases"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles."""

    class Media:
        css = {"all": ("css/admin/admin-accounts.css",)}

    list_display = ["profile_display", "user", "created_at"]

    list_display_links = ["profile_display", "user"]

    search_fields = ["user__username", "user__email", "display_name"]

    readonly_fields = ["created_at", "updated_at"]

    date_hierarchy = "created_at"

    fieldsets = (
        ("👤 User", {"fields": ("user",)}),
        ("🎨 Profile", {"fields": ("display_name", "profile_picture")}),
        (
            "📊 Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def profile_display(self, obj):
        """Display profile with avatar."""
        if obj.profile_picture:
            return format_html(
                '<div class="user-profile-display">'
                '<img src="{}" class="user-avatar" alt="{}">'
                '<span class="user-display-name">{}</span>'
                "</div>",
                obj.profile_picture.url,
                obj.get_display_name(),
                obj.get_display_name(),
            )

        initial = obj.user.username[0].upper() if obj.user.username else "?"
        return format_html(
            '<div class="user-profile-display">'
            '<div class="user-avatar-placeholder">{}</div>'
            '<span class="user-display-name">{}</span>'
            "</div>",
            initial,
            obj.get_display_name(),
        )

    profile_display.short_description = "Profile"
