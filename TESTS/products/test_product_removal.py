"""Tests for product removal behavior."""

from decimal import Decimal

import pytest
from django.urls import reverse

from products.models import Product


@pytest.mark.django_db
class TestProductRemovalAdminAction:
    """Test admin action for permanent removal of products."""

    def test_admin_remove_purchased_product_keeps_access(
        self,
        client,
        staff_user,
        verified_user,
        order_paid,
    ):
        """Purchased product is removed from public pages but remains readable for buyer."""
        product = order_paid.line_items.first().product

        client.force_login(staff_user)
        response = client.post(
            reverse("admin:products_product_changelist"),
            {
                "action": "remove_products_permanently",
                "_selected_action": [str(product.pk)],
            },
            follow=True,
        )

        assert response.status_code == 200

        product.refresh_from_db()
        assert product.is_removed is True
        assert product.is_active is False

        client.force_login(verified_user)

        archive_response = client.get(reverse("archive"))
        assert archive_response.status_code == 200
        assert product.title not in archive_response.content.decode()

        detail_response = client.get(reverse("product_detail", args=[product.slug]))
        assert detail_response.status_code == 404

        my_archive_response = client.get(reverse("my_archive"), follow=True)
        assert my_archive_response.status_code == 200
        assert product.title in my_archive_response.content.decode()

        read_response = client.get(reverse("archive_read", args=[product.slug]))
        assert read_response.status_code == 200

    def test_admin_remove_unpurchased_product_hard_deletes(
        self,
        client,
        staff_user,
        category,
    ):
        """Unpurchased product is permanently deleted by the admin action."""
        product = Product.objects.create(
            title="Unpurchased Product",
            slug="unpurchased-product",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("12.00"),
            category=category,
            is_active=True,
        )

        client.force_login(staff_user)
        response = client.post(
            reverse("admin:products_product_changelist"),
            {
                "action": "remove_products_permanently",
                "_selected_action": [str(product.pk)],
            },
            follow=True,
        )

        assert response.status_code == 200
        assert Product.objects.filter(pk=product.pk).exists() is False
