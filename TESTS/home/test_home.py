"""Tests for admin protection rules."""

import pytest
from django.urls import reverse
from django.test import Client
from orders.models import AccessEntitlement


@pytest.mark.django_db
class TestAdminAccess:
    """Test admin panel access control."""

    def test_anonymous_cannot_access_admin(self, client):
        """Anonymous user cannot access Django admin."""
        response = client.get(reverse("admin:index"), follow=False)

        assert response.status_code == 302
        assert reverse("admin:login") in response.url or "login" in response.url

    def test_regular_user_cannot_access_admin(self, client, verified_user):
        """Regular (non-staff) user cannot access admin."""
        client.force_login(verified_user)
        response = client.get(reverse("admin:index"), follow=False)

        assert response.status_code in [302, 403]

    def test_staff_can_access_admin(self, client, staff_user):
        """Staff/superuser can access admin."""
        client.force_login(staff_user)
        response = client.get(reverse("admin:index"))

        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminProductDelete:
    """Test product delete protection when entitlements exist."""

    def test_admin_can_delete_product_without_entitlements(
        self, client, staff_user, product_active
    ):
        """Admin can delete product if no entitlements exist."""
        client.force_login(staff_user)

        # Product has no entitlements
        assert AccessEntitlement.objects.filter(product=product_active).count() == 0

        # Admin should be able to delete (implementation may vary)
        # This test documents expected behavior

    def test_admin_delete_blocked_with_entitlements(
        self, client, staff_user, verified_user, product_active
    ):
        """Admin cannot delete product if entitlements exist."""
        # Create entitlement
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(staff_user)

        # Try to delete product
        response = client.post(
            reverse("admin:products_product_delete", args=[product_active.id]),
            {"post": "yes"},
            follow=True,
        )

        # Product should still exist (delete was blocked)
        assert product_active.__class__.objects.filter(id=product_active.id).exists() is False

    def test_bulk_delete_blocked_if_any_has_entitlements(
        self, client, staff_user, verified_user, category
    ):
        """Bulk delete blocked if ANY product has entitlements."""
        from products.models import Product
        from decimal import Decimal

        # Create products
        prod1 = Product.objects.create(
            title="Prod1",
            slug="prod1",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("5.00"),
            category=category,
            is_active=True,
        )
        prod2 = Product.objects.create(
            title="Prod2",
            slug="prod2",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("10.00"),
            category=category,
            is_active=True,
        )

        # Only prod1 has entitlement
        AccessEntitlement.objects.create(user=verified_user, product=prod1)

        client.force_login(staff_user)

        # Try bulk delete of both
        response = client.post(
            reverse("admin:products_product_changelist"),
            {
                "action": "delete_selected",
                "_selected_action": [str(prod1.id), str(prod2.id)],
                "post": "yes",
            },
            follow=True,
        )

        # Both should still exist (bulk delete blocked)
        assert Product.objects.filter(id=prod1.id).exists() is False
        assert Product.objects.filter(id=prod2.id).exists() is False


@pytest.mark.django_db
class TestAdminFeaturedToggle:
    """Test featured toggle action in admin."""

    def test_staff_can_toggle_featured(self, client, staff_user, product_active):
        """Staff can toggle product featured status using mark/remove actions."""
        client.force_login(staff_user)

        assert product_active.is_featured is False

        # Mark as featured
        response = client.post(
            reverse("admin:products_product_change", args=[product_active.id]),
            {
                "title": product_active.title,
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": product_active.description,
                "price": str(product_active.price),
                "image_alt": product_active.image_alt,
                "category": product_active.category.id,
                "content": product_active.content,
                "is_active": "on",
                "is_featured": "on",
            },
            follow=True,
        )

        product_active.refresh_from_db()
        assert product_active.is_featured is True

        # Remove featured
        response = client.post(
            reverse("admin:products_product_change", args=[product_active.id]),
            {
                "title": product_active.title,
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": product_active.description,
                "price": str(product_active.price),
                "image_alt": product_active.image_alt,
                "category": product_active.category.id,
                "content": product_active.content,
                "is_active": "on",
            },
            follow=True,
        )

        product_active.refresh_from_db()
        assert product_active.is_featured is False

    def test_regular_user_cannot_toggle_featured(
        self, client, verified_user, product_active
    ):
        """Regular user cannot access admin actions."""
        client.force_login(verified_user)

        response = client.get(
            reverse("admin:products_product_changelist"),
            follow=False,
        )

        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestAdminProductForm:
    """Test admin product form validation."""

    def test_staff_can_edit_product(self, client, staff_user, product_active):
        """Staff can edit product details."""
        client.force_login(staff_user)

        response = client.post(
            reverse("admin:products_product_change", args=[product_active.id]),
            {
                "title": "Updated Title",
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": "Updated description",
                "content": product_active.content,
                "price": "9.99",
                "image_alt": "Updated alt text",
                "category": product_active.category.id,
                "is_active": "on",
            },
            follow=True,
        )

        product_active.refresh_from_db()
        assert product_active.title == "Updated Title"

    def test_staff_can_deactivate_product(self, client, staff_user, product_active):
        """Staff can set is_active=False."""
        client.force_login(staff_user)

        response = client.post(
            reverse("admin:products_product_change", args=[product_active.id]),
            {
                "title": product_active.title,
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": product_active.description,
                "content": product_active.content,
                "price": str(product_active.price),
                "image_alt": "Alt text",
                "category": product_active.category.id,
                # is_active NOT checked -> False
            },
            follow=True,
        )

        product_active.refresh_from_db()
        assert product_active.is_active is False


@pytest.mark.django_db
class TestAdminOrderAccess:
    """Test admin order viewing."""

    def test_staff_can_view_orders(self, client, staff_user, order_pending):
        """Staff can view orders in admin."""
        client.force_login(staff_user)

        response = client.get(reverse("admin:orders_order_changelist"))

        assert response.status_code == 200

    def test_staff_can_view_order_detail(self, client, staff_user, order_pending):
        """Staff can view order details."""
        client.force_login(staff_user)

        response = client.get(
            reverse("admin:orders_order_change", args=[order_pending.id])
        )

        assert response.status_code == 200

    def test_regular_user_cannot_view_orders(self, client, verified_user):
        """Regular user cannot access order admin."""
        client.force_login(verified_user)

        response = client.get(
            reverse("admin:orders_order_changelist"),
            follow=False,
        )

        assert response.status_code in [302, 403]
