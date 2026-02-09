"""Tests for product access control and visibility."""

import pytest
from django.urls import reverse

from orders.models import AccessEntitlement


@pytest.mark.django_db
class TestProductAccessControl:
    """Test access control for active vs inactive products."""

    def test_active_product_visible_to_anonymous(self, client, product_active):
        """Active product is 200 for anonymous users."""
        response = client.get(
            reverse("product_detail", args=[product_active.slug])
        )

        assert response.status_code == 200
        assert product_active.title in response.content.decode()

    def test_active_product_visible_to_verified_user(
        self, client, verified_user, product_active
    ):
        """Active product is 200 for verified users."""
        client.force_login(verified_user)
        response = client.get(
            reverse("product_detail", args=[product_active.slug])
        )

        assert response.status_code == 200

    def test_inactive_product_404_for_anonymous(
        self, client, product_inactive
    ):
        """Inactive product is 404 for anonymous users."""
        response = client.get(
            reverse("product_detail", args=[product_inactive.slug])
        )

        assert response.status_code == 404

    def test_inactive_product_404_for_unentitled_user(
        self, client, verified_user, product_inactive
    ):
        """Inactive product is 404 for user without entitlement."""
        client.force_login(verified_user)
        response = client.get(
            reverse("product_detail", args=[product_inactive.slug])
        )

        assert response.status_code == 404

    def test_inactive_product_visible_to_owner_with_entitlement(
        self, client, verified_user, product_inactive, category
    ):
        """Inactive product is 200 for user with AccessEntitlement."""
        # Create entitlement
        AccessEntitlement.objects.create(
            user=verified_user, product=product_inactive
        )

        client.force_login(verified_user)
        response = client.get(
            reverse("product_detail", args=[product_inactive.slug])
        )

        assert response.status_code == 200

    def test_inactive_product_visible_to_staff(
        self, client, staff_user, product_inactive
    ):
        """Inactive product is 200 for staff/superuser."""
        client.force_login(staff_user)
        response = client.get(
            reverse("product_detail", args=[product_inactive.slug])
        )

        assert response.status_code == 200

    def test_product_list_shows_only_active(
        self, client, product_active, product_inactive
    ):
        """Product list only shows active products."""
        response = client.get(reverse("archive"))

        assert response.status_code == 200
        content = response.content.decode()
        assert product_active.title in content
        assert product_inactive.title not in content


@pytest.mark.django_db
class TestProductDetailContent:
    """Test that product detail page shows correct content."""

    def test_active_product_shows_content(self, client, product_active):
        """Active product detail shows title and description."""
        response = client.get(
            reverse("product_detail", args=[product_active.slug])
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert product_active.title in content
        assert product_active.description in content

    def test_product_shows_price(self, client, product_active):
        """Product detail shows price."""
        response = client.get(
            reverse("product_detail", args=[product_active.slug])
        )

        assert response.status_code == 200
        content = response.content.decode()
        # Price should appear somewhere (format might vary)
        assert "9.99" in content or "€" in content

    def test_inactive_product_404_even_with_old_link(
        self, client, product_inactive
    ):
        """Product marked inactive via is_active=False returns 404."""
        assert product_inactive.is_active is False

        response = client.get(
            reverse("product_detail", args=[product_inactive.slug])
        )

        assert response.status_code == 404


@pytest.mark.django_db
class TestProductListFiltering:
    """Test that product list correctly filters by status."""

    def test_featured_products_appear_in_list(self, client, category):
        """Featured products appear in product list."""
        from decimal import Decimal

        from products.models import Product

        featured = Product.objects.create(
            title="Featured",
            slug="featured",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("5.00"),
            category=category,
            is_active=True,
            is_featured=True,
        )

        response = client.get(reverse("archive"))

        assert response.status_code == 200
        assert featured.title in response.content.decode()

    def test_inactive_featured_not_in_list(self, client, category):
        """Inactive products do not appear even if featured."""
        from decimal import Decimal

        from products.models import Product

        inactive_featured = Product.objects.create(
            title="Inactive Featured",
            slug="inactive-featured",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("5.00"),
            category=category,
            is_active=False,
            is_featured=True,
        )

        response = client.get(reverse("archive"))

        assert response.status_code == 200
        assert inactive_featured.title not in response.content.decode()
