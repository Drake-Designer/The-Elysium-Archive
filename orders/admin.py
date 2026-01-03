"""Admin configuration for the orders app."""

from django.contrib import admin

from .models import AccessEntitlement, Order, OrderLineItem


class OrderLineItemInline(admin.TabularInline):
    """Display order line items within the order admin."""

    model = OrderLineItem
    extra = 0
    readonly_fields = ("product_title", "product_price", "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for orders."""

    list_display = ("order_number", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__username", "user__email")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderLineItemInline]

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "total",
                    "stripe_session_id",
                    "stripe_pid",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(OrderLineItem)
class OrderLineItemAdmin(admin.ModelAdmin):
    """Admin interface for order line items."""

    list_display = (
        "order",
        "product_title",
        "product_price",
        "quantity",
        "line_total",
    )
    list_filter = ("order__status", "order__created_at")
    search_fields = ("product_title", "order__order_number")
    readonly_fields = ("line_total",)


@admin.register(AccessEntitlement)
class AccessEntitlementAdmin(admin.ModelAdmin):
    """Admin interface for access entitlements."""

    list_display = ("user", "product", "order", "granted_at")
    list_filter = ("granted_at", "order__status")
    search_fields = (
        "user__username",
        "user__email",
        "product__title",
        "order__order_number",
    )
    readonly_fields = ("granted_at",)
