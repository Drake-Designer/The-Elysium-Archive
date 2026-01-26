"""Models for the orders app."""

from decimal import Decimal
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.contrib.auth.models import AbstractUser

class Order(models.Model):
    """Store a purchase order."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    # Type hints for fields
    order_number: models.CharField
    status: models.CharField
    total: models.DecimalField
    stripe_session_id: models.CharField
    stripe_payment_intent_id: models.CharField
    created_at: models.DateTimeField
    updated_at: models.DateTimeField

    # Django auto-generated
    id: int

    # Reverse relations
    if TYPE_CHECKING:
        line_items: "QuerySet[OrderLineItem]"
        entitlements: "QuerySet[AccessEntitlement]"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal("0.00"),
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Stripe checkout session ID for tracing",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Stripe payment intent ID for auditing",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.order_number}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Generate order number before saving."""
        if not self.order_number:
            import uuid

            self.order_number = uuid.uuid4().hex.upper()[:16]
        super().save(*args, **kwargs)

class OrderLineItem(models.Model):
    """Store individual products within an order."""

    # Type hints for fields
    product_title: models.CharField
    product_price: models.DecimalField
    quantity: models.PositiveIntegerField
    line_total: models.DecimalField

    # Django auto-generated
    id: int

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="line_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    product_title = models.CharField(max_length=120)
    product_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def __str__(self) -> str:
        return f"{self.quantity}x {self.product_title} (Order {self.order.order_number})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Calculate line total before saving."""
        self.line_total = self.product_price * self.quantity
        super().save(*args, **kwargs)

class AccessEntitlement(models.Model):
    """Grant a user access to a purchased product."""

    # Type hints for fields
    granted_at: models.DateTimeField

    # Django auto-generated
    id: int

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entitlements",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="entitlements",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entitlements",
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_entitlement_per_user_product",
            )
        ]
        ordering = ["-granted_at"]

    def __str__(self) -> str:
        return f"{self.user} -> {self.product}"
