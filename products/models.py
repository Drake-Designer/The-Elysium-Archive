from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField


class Product(models.Model):
    """Store a purchasable archive entry."""

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)

    tagline = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    content = models.TextField(
        blank=True,
        default="",
        help_text="Full archive text, visible only after purchase"
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Archive category (e.g., Lore, Rituals, Chronicles)",
    )

    price = models.DecimalField(max_digits=6, decimal_places=2)

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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the URL for the product detail page."""
        return reverse("product_detail", kwargs={"slug": self.slug})
