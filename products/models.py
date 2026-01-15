"""Product, category, and deal banner models for The Elysium Archive."""
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import MaxLengthValidator


class Category(models.Model):
    """Product category model."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """This method auto-generates slug from name when missing."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Archive entry (product) model."""
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    tagline = models.CharField(max_length=250, help_text="Short preview text")
    description = models.TextField(help_text="Public teaser description")
    content = CKEditor5Field(
        "Content",
        config_name="writer",
        help_text="Full content (visible after purchase)",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_alt = models.CharField(
        max_length=255,
        blank=True,
        validators=[MaxLengthValidator(150)],
        help_text="Recommended 60-125 chars. Max 150.",
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    is_deal = models.BooleanField(
        default=False,
        help_text="Deal status used by filters and UI",
    )
    deal_manual = models.BooleanField(
        default=False,
        help_text="This flag forces a product to be a deal",
    )
    deal_exclude = models.BooleanField(
        default=False,
        help_text="This flag excludes a product from category deal banners",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """This method saves the product and syncs deal status."""
        if not self.slug:
            self.slug = slugify(self.title)

        # Enforce model-level validation on save to ensure ORM/API saves
        # cannot bypass the 150-char image_alt constraint.
        self.full_clean()

        super().save(*args, **kwargs)
        # Recalculate only this product's deal status after save.
        sync_products_deal_status(product_pks=[self.pk])

    def get_absolute_url(self):
        """This method returns the canonical URL for this product."""
        return reverse("product_detail", kwargs={"slug": self.slug})


class DealBanner(models.Model):
    """Custom promotional banner message for the deals marquee."""
    title = models.CharField(
        max_length=100,
        help_text="Main text to display (e.g. 'DEAL', 'HOT', 'NEW')",
    )
    message = models.CharField(
        max_length=200,
        help_text="Banner message text",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Optional: Link to a specific product",
    )
    url = models.URLField(
        blank=True,
        help_text="Optional: Custom URL (used if no product is linked)",
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: Show category badge and filter by category when clicked",
    )
    icon = models.CharField(
        max_length=10,
        default="💰",
        help_text="Emoji icon (e.g. 💰, 🔥, ⭐, 🎁)",
    )
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower = first)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Deal Banner"
        verbose_name_plural = "Deal Banners"

    def __str__(self):
        return f"{self.title}: {self.message}"

    def save(self, *args, **kwargs):
        """Save banner. Deal syncing is handled by model signals and admin actions.

        Avoid running sync here to prevent duplicate recalculations when bulk
        operations or admin actions already perform updates.
        """
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete banner. Deal syncing is handled by post-delete signal.

        We avoid calling sync here to keep deletion path minimal; the
        `post_delete` signal will trigger recalculation for affected products.
        """
        super().delete(*args, **kwargs)

    def get_url(self):
        """This method returns the appropriate URL for this banner."""
        if self.product and self.product.is_active:
            return self.product.get_absolute_url()

        if self.url:
            return self.url

        archive_url = reverse("archive")

        if self.category:
            return f"{archive_url}?cat={self.category.slug}&deals=true"

        return f"{archive_url}?deals=true"


def sync_products_deal_status(product_pks=None, category_pks=None):
    """Recalculate deal status for affected products.

    To avoid expensive full-table recalculations, this function requires at
    least one of `product_pks` or `category_pks` to be provided. If both are
    empty, the function is a no-op. Use an explicit full-recalculation utility
    if needed.
    """
    product_pks = list(product_pks or [])
    category_pks = list(category_pks or [])

    # If nothing specified, skip to avoid scanning all products unintentionally.
    if not product_pks and not category_pks:
        return

    qs = Product.objects.filter(
        Q(pk__in=product_pks) | Q(category__pk__in=category_pks)
    ).select_related("category")

    active_banners = DealBanner.objects.filter(is_active=True)

    banner_product_pks = set(
        active_banners.filter(product__isnull=False).values_list("product__pk", flat=True)
    )

    banner_category_pks = set(
        active_banners.filter(category__isnull=False).values_list("category__pk", flat=True)
    )

    now = timezone.now()

    true_pks = []
    false_pks = []

    for product in qs:
        from_product_banner = product.pk in banner_product_pks
        category_pk = product.category.pk if product.category is not None else None
        from_category_banner = (category_pk in banner_category_pks) and (not product.deal_exclude)

        effective = bool(product.deal_manual or from_product_banner or from_category_banner)

        if product.is_deal and not effective:
            false_pks.append(product.pk)
        elif not product.is_deal and effective:
            true_pks.append(product.pk)

    if true_pks:
        Product.objects.filter(pk__in=true_pks).update(is_deal=True, updated_at=now)
    if false_pks:
        Product.objects.filter(pk__in=false_pks).update(is_deal=False, updated_at=now)


# Signals to ensure sync runs for save/delete events (covers bulk delete via
# QuerySet.delete which still emits post_delete per-instance).
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=DealBanner)
def deal_banner_post_save(sender, instance, created, **kwargs):
    product_pks = [instance.product.pk] if instance.product else []
    category_pks = [instance.category.pk] if instance.category else []
    if product_pks or category_pks:
        sync_products_deal_status(product_pks=product_pks, category_pks=category_pks)


@receiver(post_delete, sender=DealBanner)
def deal_banner_post_delete(sender, instance, **kwargs):
    product_pks = [instance.product.pk] if instance.product else []
    category_pks = [instance.category.pk] if instance.category else []
    if product_pks or category_pks:
        sync_products_deal_status(product_pks=product_pks, category_pks=category_pks)
