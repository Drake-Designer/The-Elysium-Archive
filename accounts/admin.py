"""Admin interface for accounts app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import UserProfile
from products.admin_utils import admin_display

User = get_user_model()


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

    list_display = (
        "username",
        "email",
        "email_verified_badge",
        "purchase_count",
        "is_staff",
        "date_joined",
    )
    # Explicit list_filter without concatenation to avoid type issues
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        HasPurchasesFilter,
    )
    
    def get_queryset(self, request):
        """Annotate users with entitlement count."""
        queryset = super().get_queryset(request)
        return queryset.annotate(entitlement_total=Count("entitlements"))

    @admin_display("Email Status")
    def email_verified_badge(self, obj):
        """Display email verification status as badge."""
        from allauth.account.models import EmailAddress
        
        verified = EmailAddress.objects.filter(
            user=obj, verified=True
        ).exists()
        
        if verified:
            return mark_safe('<span class="badge badge-success">✓ Verified</span>')
        else:
            return mark_safe('<span class="badge badge-warning">Unverified</span>')

    @admin_display("Purchases")
    def purchase_count(self, obj):
        """Display number of purchases as badge."""
        count = getattr(obj, "entitlement_total", 0) or 0
        if count > 0:
            return format_html(
                '<span class="badge badge-gold">{} purchase{}</span>',
                count,
                "s" if count != 1 else "",
            )
        return "-"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles."""

    list_display = ("user", "display_name", "created_at")
    search_fields = ("user__username", "user__email", "display_name")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("User", {"fields": ("user",)}),
        ("Profile", {"fields": ("display_name", "profile_picture")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
