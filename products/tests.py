"""Tests for Product model CRUD operations and permissions."""

import pytest
from django.contrib.auth import get_user_model
from products.models import Product


User = get_user_model()


@pytest.mark.django_db
class TestProductCRUD:
    """Test CRUD operations on Product model."""

    def setup_method(self):
        """Create test data."""
        self.product = Product.objects.create(
            title="Test Forbidden Knowledge",
            slug="test-forbidden",
            description="A test product",
            price=29.99,
            image_alt="A forbidden artifact",
            is_active=True,
        )

    def test_create_product(self):
        """Test creating a product."""
        product = Product.objects.create(
            title="New Relic",
            slug="new-relic",
            description="A forbidden artifact",
            price=49.99,
            image_alt="New relic image",
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
        from decimal import Decimal

        self.product.price = Decimal("39.99")
        self.product.save()
        product = Product.objects.get(pk=self.product.pk)
        assert float(product.price) == 39.99

    def test_delete_product(self):
        """Test deleting a product."""
        product_id = self.product.pk
        self.product.delete()
        assert not Product.objects.filter(pk=product_id).exists()
