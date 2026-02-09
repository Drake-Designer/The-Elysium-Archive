"""Admin configuration for the orders app."""

from django.contrib import admin
from django.db import transaction
from django.utils.html import format_html

from .models import AccessEntitlement, Order, OrderLineItem


class OrderLineItemInline(admin.TabularInline):
    """Display order line items within the order admin."""

    model = OrderLineItem
    extra = 0
    readonly_fields = [
        "product_title",
        "product_price",
        "quantity",
        "line_total",
    ]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders."""

    class Media:
        css = {
            "all": ("css/admin/admin-orders.css",),
        }

    list_display = [
        "order_number_display",
        "user_display",
        "email_display",
        "status_badge",
        "total_display",
        "created_at",
    ]

    list_display_links = ["order_number_display"]
    list_filter = ["status"]
    search_fields = ["order_number", "user__username", "user__email"]
    readonly_fields = ["order_number", "created_at", "updated_at"]
    inlines = [OrderLineItemInline]
    date_hierarchy = "created_at"

    fieldsets = [
        (
            "Order Information",
            {
                "fields": ("order_number", "user", "status", "total"),
            },
        ),
        (
            "Payment Details",
            {
                "fields": ("stripe_session_id", "stripe_payment_intent_id"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    ]

    actions = ["mark_as_paid", "mark_as_failed"]

    def order_number_display(self, obj):
        """Display order number with styling."""
        return format_html(
            '<code class="order-number-display">#{}</code>',
            obj.order_number,
        )

    order_number_display.short_description = "Order"

    def user_display(self, obj):
        """Display username."""
        if obj.user:
            return format_html(
                '<span class="order-username">{}</span>',
                obj.user.username,
            )
        return format_html('<span class="order-no-user">Guest</span>')

    user_display.short_description = "User"

    def email_display(self, obj):
        """Display user email."""
        if obj.user:
            return format_html(
                '<span class="order-email">{}</span>',
                obj.user.email,
            )
        return format_html('<span class="text-muted">-</span>')

    email_display.short_description = "Email"

    def status_badge(self, obj):
        """Display order status with colored badge."""
        return format_html(
            '<span class="order-status-badge {}">{}</span>',
            obj.status,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"

    def total_display(self, obj):
        """Display order total with styling."""
        return format_html(
            '<span class="order-total-display">€{}</span>',
            obj.total,
        )

    total_display.short_description = "Total"

    def mark_as_paid(self, request, queryset):
        """Mark orders as paid."""
        updated = 0
        granted = 0
        skipped_no_user = 0

        for order in queryset.select_related("user").prefetch_related(
            "line_items__product"
        ):
            with transaction.atomic():
                locked = Order.objects.select_for_update().get(pk=order.pk)

                if locked.status != "paid":
                    locked.status = "paid"
                    locked.save(update_fields=["status", "updated_at"])
                    updated += 1

                if not locked.user:
                    skipped_no_user += 1
                    continue

                for line_item in locked.line_items.all():
                    if not line_item.product:
                        continue

                    _, created = AccessEntitlement.objects.get_or_create(
                        user=locked.user,
                        product=line_item.product,
                        defaults={"order": locked},
                    )
                    if created:
                        granted += 1

        self.message_user(
            request,
            (
                f"{updated} orders marked as paid. "
                f"{granted} access entitlements granted. "
                f"{skipped_no_user} orders had no user."
            ),
        )

    mark_as_paid.short_description = "Mark as paid"

    def mark_as_failed(self, request, queryset):
        """Mark orders as failed."""
        updated = queryset.update(status="failed")
        self.message_user(request, f"{updated} orders marked as failed.")

    mark_as_failed.short_description = "Mark as failed"


@admin.register(AccessEntitlement)
class AccessEntitlementAdmin(admin.ModelAdmin):
    """Admin interface for access entitlements."""

    class Media:
        css = {
            "all": ("css/admin/admin-orders.css",),
        }

    list_display = [
        "user_display",
        "email_display",
        "product",
        "order",
        "granted_badge",
    ]

    list_display_links = ["user_display", "product"]
    list_filter = ["order__status"]
    search_fields = [
        "user__username",
        "user__email",
        "product__title",
        "order__order_number",
    ]
    readonly_fields = ["granted_at"]
    date_hierarchy = "granted_at"

    def user_display(self, obj):
        """Display username."""
        return format_html(
            '<span class="order-username">{}</span>',
            obj.user.username,
        )

    user_display.short_description = "User"

    def email_display(self, obj):
        """Display user email."""
        return format_html(
            '<span class="order-email">{}</span>',
            obj.user.email,
        )

    email_display.short_description = "Email"

    def granted_badge(self, obj):
        """Display granted date with badge."""
        return format_html(
            '<span class="entitlement-granted-badge">{}</span>',
            obj.granted_at.strftime("%b %d, %Y"),
        )

    granted_badge.short_description = "Granted"
