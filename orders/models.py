"""Models for the orders app."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product


class Order(models.Model):
    """Store a completed purchase order."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        """Generate order number before saving."""
        if not self.order_number:
            import uuid

            self.order_number = uuid.uuid4().hex.upper()[:16]
        super().save(*args, **kwargs)


class OrderLineItem(models.Model):
    """Store individual products within an order."""

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

    def __str__(self):
        return (
            f"{self.quantity}x {self.product_title} (Order {self.order.order_number})"
        )

    def save(self, *args, **kwargs):
        """Calculate line total before saving."""
        self.line_total = self.product_price * self.quantity
        super().save(*args, **kwargs)
