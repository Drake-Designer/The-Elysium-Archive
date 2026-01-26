"""Models for the reviews app."""

from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from products.models import Product

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

class Review(models.Model):
    """Store a verified buyer review for a purchased product."""

    RATING_CHOICES = [
        (1, "1 - Poor"),
        (2, "2 - Fair"),
        (3, "3 - Good"),
        (4, "4 - Excellent"),
        (5, "5 - Outstanding"),
    ]

    user: models.ForeignKey
    product: models.ForeignKey
    rating: models.PositiveIntegerField
    title: models.CharField
    body: models.TextField
    created_at: models.DateTimeField
    updated_at: models.DateTimeField

    # Django auto-generated
    id: int

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional review title",
    )
    body = models.TextField(
        help_text="Share your thoughts about this archive entry",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="unique_review_per_user_product"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} reviewed {self.product}"
