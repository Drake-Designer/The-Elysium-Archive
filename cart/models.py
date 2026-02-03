"""Models for the cart app."""

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from products.models import Product

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class Cart(models.Model):
    """Store a persistent cart for a user."""

    user: models.OneToOneField["AbstractUser"]
    updated_at: models.DateTimeField

    # Django auto-generated
    id: int

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart for {self.user}"


class CartItem(models.Model):
    """Store a product entry in a persistent cart."""

    cart: models.ForeignKey["Cart"]
    product: models.ForeignKey[Product]
    quantity: models.PositiveSmallIntegerField

    # Django auto-generated
    id: int

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product} in {self.cart}"
