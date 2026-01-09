"""Admin configuration for the reviews app."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for reviews."""
    
    class Media:
        css = {
            'all': ('css/admin/admin-reviews.css',)
        }

    list_display = [
        'rating_display',
        'user_display',
        'product',
        'title_display',
        'verified_badge',
        'created_at'
    ]
    
    list_display_links = ['title_display']
    
    list_filter = ['rating', 'created_at', 'product']
    
    search_fields = ['user__username', 'user__email', 'product__title', 'title', 'body']
    
    readonly_fields = ['created_at', 'updated_at', 'full_review_preview']
    
    date_hierarchy = 'created_at'

    fieldsets = (
        ('⭐ Review Information', {
            'fields': ('user', 'product', 'rating', 'title'),
        }),
        ('📝 Content', {
            'fields': ('body',),
        }),
        ('👁️ Preview', {
            'fields': ('full_review_preview',),
        }),
        ('📊 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['delete_selected']
    
    def rating_display(self, obj):
        """Display star rating."""
        full_stars = obj.rating
        empty_stars = 5 - obj.rating
        
        stars_html = ''.join(['<span class="review-star">★</span>' for _ in range(full_stars)])
        stars_html += ''.join(['<span class="review-star empty">☆</span>' for _ in range(empty_stars)])
        
        return format_html(
            '<div class="review-rating-display">{}<span class="review-rating-text">{}/5</span></div>',
            stars_html,
            obj.rating
        )
    rating_display.short_description = 'Rating'
    
    def user_display(self, obj):
        """Display user with email."""
        return format_html(
            '<div class="order-user-info">'
            '<span class="order-username">{}</span>'
            '<span class="order-email">{}</span>'
            '</div>',
            obj.user.username,
            obj.user.email
        )
    user_display.short_description = 'User'
    
    def title_display(self, obj):
        """Display review title or first words of body."""
        if obj.title:
            return format_html(
                '<div class="review-title-display">{}</div>',
                obj.title
            )
        preview = obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
        return format_html(
            '<div class="review-body-preview">{}</div>',
            preview
        )
    title_display.short_description = 'Title/Preview'
    
    def verified_badge(self, obj):
        """Check if user has purchased the product."""
        has_purchased = obj.user.entitlements.filter(product=obj.product).exists()
        
        if has_purchased:
            return mark_safe(
                '<span class="review-verified-badge">✓ Verified Purchase</span>'
            )
        return mark_safe('<span class="badge-muted">Not Verified</span>')
    verified_badge.short_description = 'Status'
    
    def full_review_preview(self, obj):
        """Display full review preview in form."""
        if not obj.pk:
            return "Save the review to see preview"
        
        full_stars = obj.rating
        empty_stars = 5 - obj.rating
        stars_html = '⭐' * full_stars + '☆' * empty_stars
        
        return format_html(
            '<div style="background-color: var(--admin-panel); padding: 20px; border-radius: 8px; border: 1px solid var(--admin-border);">'
            '<div style="margin-bottom: 12px;">'
            '<span style="font-size: 20px;">{}</span>'
            '<span style="margin-left: 8px; font-weight: 600; color: var(--admin-gold);">{}/5</span>'
            '</div>'
            '<h3 style="color: var(--admin-text); margin-bottom: 8px;">{}</h3>'
            '<p style="color: var(--admin-muted); line-height: 1.6;">{}</p>'
            '<div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--admin-border);">'
            '<small style="color: var(--admin-muted);">By {} on {}</small>'
            '</div>'
            '</div>',
            stars_html,
            obj.rating,
            obj.title or '(No title)',
            obj.body,
            obj.user.username,
            obj.created_at.strftime('%b %d, %Y')
        )
    full_review_preview.short_description = 'Review Preview'
