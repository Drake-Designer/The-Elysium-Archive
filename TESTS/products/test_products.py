"""Tests for Product model CRUD operations and permissions."""

from decimal import Decimal

import pytest
from django.urls import reverse

from products.models import Category, Product


@pytest.mark.django_db
class TestProductCRUD:
    """Test CRUD operations on Product model."""

    def setup_method(self):
        """Create test data."""
        self.category = Category.objects.create(
            name="Test Lore", slug="test-lore"
        )

        self.product = Product.objects.create(
            title="Test Forbidden Knowledge",
            slug="test-forbidden",
            tagline="Test tagline",
            description="A test product",
            content="<p>Test premium content.</p>",
            price=Decimal("29.99"),
            image_alt="A forbidden artifact",
            category=self.category,
            is_active=True,
        )

    def test_create_product(self):
        """Test creating a product."""
        assert Product.objects.filter(slug="test-forbidden").exists()

    def test_read_product(self):
        """Test reading a product."""
        product = Product.objects.get(slug="test-forbidden")
        assert product.title == "Test Forbidden Knowledge"

    def test_update_product(self):
        """Test updating a product."""
        self.product.title = "Updated Title"
        self.product.save()
        updated = Product.objects.get(slug="test-forbidden")
        assert updated.title == "Updated Title"

    def test_unpublish_product(self):
        """Test unpublishing a product instead of deleting it."""
        product_id = self.product.pk
        self.product.is_active = False
        self.product.save(update_fields=["is_active", "updated_at"])

        assert Product.objects.filter(pk=product_id).exists()
        assert Product.objects.get(pk=product_id).is_active is False


@pytest.mark.django_db
def test_archive_cards_use_flex_alignment(client, product_active):
    """Archive cards use flex layout so CTAs align across cards."""
    response = client.get(reverse("archive"))
    assert response.status_code == 200
    html = response.content.decode()

    assert "flex-grow-1" in html
    assert "mt-auto" in html
