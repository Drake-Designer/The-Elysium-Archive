from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from reviews.models import Review


class Category(models.Model):
    """Group archives by domain."""

    name: models.CharField
    slug: models.SlugField
    description: models.TextField
    created_at: models.DateTimeField
    updated_at: models.DateTimeField
    
    # Django auto-generated
    id: int
    
    # Reverse relations
    if TYPE_CHECKING:
        products: "QuerySet[Product]"

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Store a purchasable archive entry."""

    # Type hints per attributi field
    title: models.CharField
    slug: models.SlugField
    tagline: models.CharField
    description: models.TextField
    content: CKEditor5Field
    price: models.DecimalField
    image: CloudinaryField
    image_alt: models.CharField
    is_active: models.BooleanField
    is_featured: models.BooleanField
    created_at: models.DateTimeField
    updated_at: models.DateTimeField
    
    # Django auto-generated
    id: int
    
    # Reverse relation - FUORI dal blocco runtime!
    if TYPE_CHECKING:
        reviews: "QuerySet[Review]"

    # Definizioni runtime
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    tagline = models.CharField(max_length=120, blank=True)
    description = models.TextField()

    content = CKEditor5Field(
        blank=True,
        default="",
        config_name="product_content",
        help_text="Full archive text, visible only after purchase",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True,
        help_text="Archive category such as Lore, Rituals, or Chronicles",
    )

    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price must be a positive value",
    )

    image = CloudinaryField("image", blank=True, null=True)

    image_alt = models.CharField(
        max_length=255, help_text="Describe the image for accessibility and SEO"
    )

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """Return the URL for the product detail page."""
        return reverse("product_detail", kwargs={"slug": self.slug})
