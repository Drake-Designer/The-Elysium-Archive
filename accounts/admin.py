"""Admin interface for accounts app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import UserProfile

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
    
    class Media:
        css = {
            'all': ('css/admin/admin-accounts.css',)
        }

    list_display = (
        "user_display",
        "email",
        "email_verified_badge",
        "purchase_count",
        "role_badges",
        "date_joined",
    )
    
    list_display_links = ("user_display",)
    
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        HasPurchasesFilter,
    )
    
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_queryset(self, request):
        """Annotate users with entitlement count."""
        queryset = super().get_queryset(request)
        return queryset.annotate(entitlement_total=Count("entitlements"))
    
    def user_display(self, obj):
        """Display user with avatar/placeholder."""
        # Try to get profile picture
        try:
            if hasattr(obj, 'profile') and obj.profile.profile_picture:
                return format_html(
                    '<div class="user-profile-display">'
                    '<img src="{}" class="user-avatar" alt="{}">'
                    '<div class="user-info">'
                    '<span class="user-display-name">{}</span>'
                    '<span class="user-username">@{}</span>'
                    '</div>'
                    '</div>',
                    obj.profile.profile_picture.url,
                    obj.username,
                    obj.profile.get_display_name(),
                    obj.username
                )
        except:
            pass
        
        # Fallback: first letter avatar
        initial = obj.username[0].upper() if obj.username else '?'
        return format_html(
            '<div class="user-profile-display">'
            '<div class="user-avatar-placeholder">{}</div>'
            '<div class="user-info">'
            '<span class="user-display-name">{}</span>'
            '<span class="user-username">@{}</span>'
            '</div>'
            '</div>',
            initial,
            obj.get_full_name() or obj.username,
            obj.username
        )
    user_display.short_description = 'User'

    def email_verified_badge(self, obj):
        """Display email verification status as badge."""
        try:
            from allauth.account.models import EmailAddress
            verified = EmailAddress.objects.filter(
                user=obj, verified=True
            ).exists()
        except:
            verified = False
        
        if verified:
            return mark_safe('<span class="badge-success">✓ Verified</span>')
        else:
            return mark_safe('<span class="badge-warning">⚠ Unverified</span>')
    email_verified_badge.short_description = 'Email'

    def purchase_count(self, obj):
        """Display number of purchases as badge."""
        count = getattr(obj, "entitlement_total", 0) or 0
        if count > 0:
            return format_html(
                '<span class="badge-gold">{} purchase{}</span>',
                count,
                "s" if count != 1 else "",
            )
        return mark_safe('<span class="badge-muted">No purchases</span>')
    purchase_count.short_description = 'Purchases'
    
    def role_badges(self, obj):
        """Display staff/superuser badges."""
        badges = []
        
        if obj.is_superuser:
            badges.append('<span class="user-role-badge superuser">👑 SUPERUSER</span>')
        elif obj.is_staff:
            badges.append('<span class="user-role-badge staff">🛡️ STAFF</span>')
        
        if not badges:
            return mark_safe('<span class="badge-muted">User</span>')
        
        return mark_safe(''.join(badges))
    role_badges.short_description = 'Role'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for user profiles."""
    
    class Media:
        css = {
            'all': ('css/admin/admin-accounts.css',)
        }

    list_display = [
        "profile_display",
        "user",
        "created_at"
    ]
    
    list_display_links = ["profile_display", "user"]
    
    search_fields = ["user__username", "user__email", "display_name"]
    
    readonly_fields = ["created_at", "updated_at", "profile_preview"]
    
    fieldsets = (
        ('👤 User', {
            'fields': ('user',)
        }),
        ('🎨 Profile', {
            'fields': ('display_name', 'profile_picture')
        }),
        ('👁️ Preview', {
            'fields': ('profile_preview',)
        }),
        ('📊 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def profile_display(self, obj):
        """Display profile with avatar."""
        if obj.profile_picture:
            return format_html(
                '<div class="user-profile-display">'
                '<img src="{}" class="user-avatar" alt="{}">'
                '<span class="user-display-name">{}</span>'
                '</div>',
                obj.profile_picture.url,
                obj.get_display_name(),
                obj.get_display_name()
            )
        
        initial = obj.user.username[0].upper() if obj.user.username else '?'
        return format_html(
            '<div class="user-profile-display">'
            '<div class="user-avatar-placeholder">{}</div>'
            '<span class="user-display-name">{}</span>'
            '</div>',
            initial,
            obj.get_display_name()
        )
    profile_display.short_description = 'Profile'
    
    def profile_preview(self, obj):
        """Display profile preview."""
        if not obj.pk:
            return "Save the profile to see preview"
        
        if obj.profile_picture:
            avatar_html = format_html(
                '<img src="{}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid var(--admin-gold-border);" alt="{}">',
                obj.profile_picture.url,
                obj.get_display_name()
            )
        else:
            initial = obj.user.username[0].upper() if obj.user.username else '?'
            avatar_html = format_html(
                '<div style="width: 80px; height: 80px; border-radius: 50%; background-color: var(--admin-gold-soft); border: 3px solid var(--admin-gold-border); display: flex; align-items: center; justify-content: center; color: var(--admin-gold); font-weight: 700; font-size: 32px;">{}</div>',
                initial
            )
        
        return format_html(
            '<div style="background-color: var(--admin-panel); padding: 20px; border-radius: 8px; border: 1px solid var(--admin-border); display: flex; align-items: center; gap: 20px;">'
            '{}'
            '<div>'
            '<h3 style="color: var(--admin-text); margin: 0 0 8px 0;">{}</h3>'
            '<p style="color: var(--admin-muted); margin: 0;">@{}</p>'
            '<p style="color: var(--admin-muted); margin: 8px 0 0 0; font-size: 14px;">{}</p>'
            '</div>'
            '</div>',
            avatar_html,
            obj.get_display_name(),
            obj.user.username,
            obj.user.email
        )
    profile_preview.short_description = 'Profile Preview'
