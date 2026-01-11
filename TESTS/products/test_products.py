"""Tests for Product model CRUD operations and permissions."""

import pytest
from decimal import Decimal
from products.models import Category, Product


@pytest.mark.django_db
class TestProductCRUD:
    """Test CRUD operations on Product model."""

    def setup_method(self):
        """Create test data."""
        self.category = Category.objects.create(name="Test Lore", slug="test-lore")

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
        product = Product.objects.create(
            title="New Relic",
            slug="new-relic",
            tagline="Test tagline",
            description="A forbidden artifact",
            content="<p>Test premium content.</p>",
            price=Decimal("49.99"),
            image_alt="New relic image",
            category=self.category,
            is_active=True,
        )
        assert product.pk is not None
        assert product.title == "New Relic"

    def test_read_product(self):
        """Test reading a product from database."""
        product = Product.objects.get(pk=self.product.pk)
        assert product.title == "Test Forbidden Knowledge"
        assert float(product.price) == 29.99

    def test_update_product(self):
        """Test updating a product."""
        self.product.price = Decimal("39.99")
        self.product.save()
        product = Product.objects.get(pk=self.product.pk)
        assert float(product.price) == 39.99

    def test_delete_product(self):
        """Test deleting a product."""
        product_id = self.product.pk
        self.product.delete()
        assert not Product.objects.filter(pk=product_id).exists()
