"""Product, category, and deal banner models."""

from decimal import Decimal

from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


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
        """Auto-generate slug from name when missing."""
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
        help_text="Full content visible after purchase",
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
    is_removed = models.BooleanField(
        default=False,
        help_text="Removed from the public site but retained for entitled users.",
    )
    is_featured = models.BooleanField(default=False)
    is_deal = models.BooleanField(
        default=False,
        help_text="Deal status (used by filters and UI)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Save the product and sync deal and featured status when needed."""
        update_fields = kwargs.get("update_fields")
        update_fields_set = set(update_fields) if update_fields else None

        is_create = self.pk is None

        # Check if we're in a sync operation to avoid recursion
        skip_sync = kwargs.pop("_skip_featured_sync", False)

        if not self.slug:
            self.slug = slugify(self.title)

        if self.is_removed:
            self.is_active = False

        # Validate fields before saving
        validate_fields = {"image_alt", "title", "slug"}
        should_validate = (
            is_create
            or update_fields_set is None
            or bool(update_fields_set & validate_fields)
        )
        if should_validate:
            self.full_clean()

        # Track if is_featured or category changed (before saving)
        is_featured_changed = False
        category_changed = False
        old_is_featured = None

        if not is_create and self.pk:
            try:
                old_product = Product.objects.get(pk=self.pk)
                old_is_featured = old_product.is_featured
                is_featured_changed = old_is_featured != self.is_featured

                # Track category change
                old_category_pk = (
                    old_product.category.pk if old_product.category else None
                )
                new_category_pk = self.category.pk if self.category else None
                category_changed = old_category_pk != new_category_pk
            except Product.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Sync deal status if category changed
        deal_fields = {"category", "category_id"}
        should_sync_deals = (
            is_create
            or update_fields_set is None
            or bool(update_fields_set & deal_fields)
        )
        if should_sync_deals:
            sync_products_deal_status(product_pks=[self.pk])

        # Sync featured status to banners if is_featured changed and not in sync mode
        if is_featured_changed and not skip_sync:
            sync_product_featured_to_banners(
                product_pk=self.pk, is_featured=self.is_featured
            )

        # Sync featured status from category banner if category changed
        if category_changed and not skip_sync:
            sync_product_featured_from_category_banner(product_pk=self.pk)

    def get_absolute_url(self):
        """Return the canonical URL for this product."""
        return reverse("product_detail", kwargs={"slug": self.slug})

    def get_discount_percentage(self):
        """Get the discount percentage for this product from active deal banners.

        Returns the percentage as an integer (e.g., 20 for 20%).
        """
        if not self.is_deal:
            return 0

        active_banners = DealBanner.objects.filter(is_active=True)

        # Check product-specific banners first
        product_banner = active_banners.filter(product=self).first()
        if product_banner and product_banner.discount_percentage > 0:
            return int(product_banner.discount_percentage)

        # Check category banners if product has a category
        if self.category:
            category_banner = active_banners.filter(category=self.category).first()
            if category_banner and category_banner.discount_percentage > 0:
                return int(category_banner.discount_percentage)

        return 0

    def get_discounted_price(self):
        """Calculate and return the discounted price.

        Returns a Decimal with 2 decimal places.
        """
        discount_percentage = self.get_discount_percentage()
        if discount_percentage > 0:
            discount_amount = self.price * Decimal(discount_percentage) / Decimal(100)
            discounted_price = self.price - discount_amount
            return discounted_price.quantize(Decimal("0.01"))
        return self.price


class DealBanner(models.Model):
    """Custom promotional banner message for the deals marquee."""

    title = models.CharField(
        max_length=100,
        help_text="Main text to display (e.g. DEAL, HOT, NEW)",
    )
    message = models.CharField(
        max_length=200,
        help_text="Banner message text",
    )
    product = models.ForeignKey(
        Product,
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
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: Show category badge and filter by category when clicked",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount percentage 0-100. Applied to linked product or category products.",
    )
    icon = models.CharField(
        max_length=10,
        default="💰",
        help_text="Emoji icon (e.g. 💰, 🔥, ⚡, ✨)",
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(
        default=True,
        help_text="Featured banners appear first in the carousel",
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower first)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_featured", "order", "-created_at"]
        verbose_name = "Deal Banner"
        verbose_name_plural = "Deal Banners"

    def __str__(self):
        return f"{self.title}: {self.message}"

    def save(self, *args, **kwargs):
        """Save banner and sync featured status with linked product/category."""
        is_create = self.pk is None

        # Check if we're in a sync operation to avoid recursion
        skip_sync = kwargs.pop("_skip_featured_sync", False)

        # Track if is_featured, is_active, or category changed (before saving)
        is_featured_changed = False
        is_active_changed = False
        old_is_featured = None
        old_is_active = None
        old_category_pk = None

        if not is_create and self.pk:
            try:
                old_banner = DealBanner.objects.get(pk=self.pk)
                old_is_featured = old_banner.is_featured
                old_is_active = old_banner.is_active
                old_category_pk = (
                    old_banner.category.pk if old_banner.category else None
                )

                is_featured_changed = old_is_featured != self.is_featured
                is_active_changed = old_is_active != self.is_active
            except DealBanner.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if not skip_sync:
            # Determine if the banner should make products featured
            # Only if BOTH is_active AND is_featured are True
            should_be_featured = self.is_featured and self.is_active

            # Sync featured status to product if banner is linked to a product
            if self.product and (is_create or is_featured_changed or is_active_changed):
                sync_banner_featured_to_product(product_pk=self.product.pk)

            # Sync featured status to category products if banner is linked to a category
            if self.category and (
                is_create or is_featured_changed or is_active_changed
            ):
                sync_category_banner_featured_to_products(
                    category_pk=self.category.pk, is_featured=should_be_featured
                )

            # If category changed, remove featured from old category products
            if old_category_pk and old_category_pk != (
                self.category.pk if self.category else None
            ):
                # Check if old category still has other active featured banners
                has_other_featured = (
                    DealBanner.objects.filter(
                        category_id=old_category_pk, is_active=True, is_featured=True
                    )
                    .exclude(pk=self.pk)
                    .exists()
                )

                if not has_other_featured:
                    sync_category_banner_featured_to_products(
                        category_pk=old_category_pk, is_featured=False
                    )

    def delete(self, *args, **kwargs):
        """Delete banner and sync featured status with product/category."""
        product_pk = self.product.pk if self.product else None
        category_pk = self.category.pk if self.category else None

        super().delete(*args, **kwargs)

        # Sync featured status after deletion
        if product_pk:
            sync_banner_featured_to_product(product_pk=product_pk)

        if category_pk:
            # Check if category still has other active featured banners
            has_other_featured_banners = DealBanner.objects.filter(
                category_id=category_pk, is_active=True, is_featured=True
            ).exists()

            if not has_other_featured_banners:
                # Remove featured from all products in category
                sync_category_banner_featured_to_products(
                    category_pk=category_pk, is_featured=False
                )

    def get_url(self):
        """Return the appropriate URL for this banner."""
        if self.product and self.product.is_active and not self.product.is_removed:
            return self.product.get_absolute_url()

        if self.url:
            return self.url

        archive_url = reverse("archive")

        if self.category:
            return f"{archive_url}?cat={self.category.slug}&deals=true"

        return f"{archive_url}?deals=true"


def sync_products_deal_status(product_pks=None, category_pks=None):
    """Recalculate deal status for affected products."""
    product_pks = list(product_pks or [])
    category_pks = list(category_pks or [])

    if not product_pks and not category_pks:
        return

    # Get products to update
    qs = (
        Product.objects.filter(Q(pk__in=product_pks) | Q(category__pk__in=category_pks))
        .filter(is_removed=False)
        .select_related("category")
    )

    # Get active banners
    active_banners = DealBanner.objects.filter(is_active=True)
    banner_product_pks = set(
        active_banners.filter(product__isnull=False).values_list(
            "product__pk", flat=True
        )
    )
    banner_category_pks = set(
        active_banners.filter(category__isnull=False).values_list(
            "category__pk", flat=True
        )
    )

    now = timezone.now()
    true_pks = []
    false_pks = []

    for product in qs:
        # Check if product is linked to a banner
        from_product_banner = product.pk in banner_product_pks

        # Check if product's category is linked to a banner
        category_pk = product.category.pk if product.category is not None else None
        from_category_banner = category_pk in banner_category_pks

        # Product is a deal if either condition is true
        effective = from_product_banner or from_category_banner

        if product.is_deal and not effective:
            false_pks.append(product.pk)
        elif not product.is_deal and effective:
            true_pks.append(product.pk)

    # Bulk update
    if true_pks:
        Product.objects.filter(pk__in=true_pks).update(is_deal=True, updated_at=now)
    if false_pks:
        Product.objects.filter(pk__in=false_pks).update(is_deal=False, updated_at=now)


def sync_banner_featured_to_product(product_pk):
    """Sync featured status from banners to product."""
    try:
        product = Product.objects.get(pk=product_pk)
    except Product.DoesNotExist:
        return

    if product.is_removed:
        if product.is_featured:
            product.is_featured = False
            product.save(
                update_fields=["is_featured", "updated_at"], _skip_featured_sync=True
            )
        return

    # Check if product has any active AND featured banners
    has_featured_banner = DealBanner.objects.filter(
        product=product, is_active=True, is_featured=True
    ).exists()

    # Update product featured status if needed
    if has_featured_banner and not product.is_featured:
        product.is_featured = True
        product.save(
            update_fields=["is_featured", "updated_at"], _skip_featured_sync=True
        )
    elif not has_featured_banner and product.is_featured:
        # Only remove featured if product has at least one active banner
        has_any_banner = DealBanner.objects.filter(
            product=product, is_active=True
        ).exists()

        if has_any_banner:
            product.is_featured = False
            product.save(
                update_fields=["is_featured", "updated_at"], _skip_featured_sync=True
            )


def sync_product_featured_to_banners(product_pk, is_featured):
    """Sync featured status from product to its banners."""
    # Get all active banners linked to this product
    banners = DealBanner.objects.filter(product_id=product_pk, is_active=True)

    # Update each banner individually to trigger save() and avoid recursion
    for banner in banners:
        if banner.is_featured != is_featured:
            banner.is_featured = is_featured
            banner.save(_skip_featured_sync=True)


def sync_category_banner_featured_to_products(category_pk, is_featured):
    """Sync featured status from category banner to all active products in category."""
    products = Product.objects.filter(
        category_id=category_pk,
        is_active=True,
        is_removed=False,
    )

    for product in products:
        if product.is_featured != is_featured:
            product.is_featured = is_featured
            product.save(
                update_fields=["is_featured", "updated_at"], _skip_featured_sync=True
            )


def sync_product_featured_from_category_banner(product_pk):
    """Check if product should be featured based on its category's banner."""
    try:
        product = Product.objects.select_related("category").get(pk=product_pk)
    except Product.DoesNotExist:
        return

    if product.is_removed:
        return

    if not product.category:
        return

    # Check if category has any active AND featured banners
    has_featured_category_banner = DealBanner.objects.filter(
        category=product.category, is_active=True, is_featured=True
    ).exists()

    # Update product featured status if needed
    if has_featured_category_banner and not product.is_featured:
        product.is_featured = True
        product.save(
            update_fields=["is_featured", "updated_at"], _skip_featured_sync=True
        )
    elif not has_featured_category_banner and product.is_featured:
        # Only remove featured if no other reason to be featured (e.g., product banner)
        has_product_banner = DealBanner.objects.filter(
            product=product, is_active=True, is_featured=True
        ).exists()

        if not has_product_banner:
            product.is_featured = False
            product.save(
                update_fields=["is_featured", "updated_at"], _skip_featured_sync=True
            )


# Signals
@receiver(post_save, sender=DealBanner)
def deal_banner_post_save(sender, instance, created, **kwargs):
    """Sync product deal status when a banner is created or updated."""
    product_pks = [instance.product.pk] if instance.product else []
    category_pks = [instance.category.pk] if instance.category else []

    if product_pks or category_pks:
        sync_products_deal_status(product_pks=product_pks, category_pks=category_pks)


@receiver(post_delete, sender=DealBanner)
def deal_banner_post_delete(sender, instance, **kwargs):
    """Sync product deal status when a banner is deleted."""
    product_pks = [instance.product.pk] if instance.product else []
    category_pks = [instance.category.pk] if instance.category else []

    if product_pks or category_pks:
        sync_products_deal_status(product_pks=product_pks, category_pks=category_pks)
