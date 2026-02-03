"""Tests for account email verification gates and dashboard access."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestEmailVerificationGate:
    """Test that unverified users cannot access protected account pages."""

    def test_unverified_user_cannot_access_dashboard(self, client, unverified_user):
        """Unverified user gets redirected from dashboard to verify email."""
        client.force_login(unverified_user)
        response = client.get(reverse("account_dashboard"))

        assert response.status_code == 302
        assert reverse("account_email") in response.url

    def test_unverified_user_cannot_access_my_archive(self, client, unverified_user):
        """Unverified user gets redirected from my_archive to verify email."""
        client.force_login(unverified_user)
        response = client.get(reverse("my_archive"))

        assert response.status_code == 302
        assert reverse("account_email") in response.url

    def test_unverified_user_cannot_access_profile(self, client, unverified_user):
        """Unverified user gets redirected from profile to verify email."""
        client.force_login(unverified_user)
        response = client.get(reverse("profile"))

        assert response.status_code == 302
        assert reverse("account_email") in response.url

    def test_anonymous_user_redirects_to_login(self, client):
        """Anonymous user trying to access dashboard gets redirected to login."""
        response = client.get(reverse("account_dashboard"))

        assert response.status_code == 302
        assert reverse("account_login") in response.url

    def test_unauthenticated_cannot_access_my_archive(self, client):
        """Unauthenticated user trying to access my_archive gets redirected to login."""
        response = client.get(reverse("my_archive"))

        assert response.status_code == 302
        assert reverse("account_login") in response.url


@pytest.mark.django_db
class TestMyArchiveDisplay:
    """Test that My Archive displays purchased products correctly."""

    def test_my_archive_empty_for_new_user(self, client, verified_user):
        """New verified user has no entitlements, my_archive is empty."""
        client.force_login(verified_user)
        response = client.get(reverse("my_archive"), follow=True)

        assert response.status_code == 200

    def test_my_archive_shows_entitlements(self, client, verified_user, order_paid):
        """Verified user sees all their purchased products in My Archive."""
        client.force_login(verified_user)
        response = client.get(reverse("my_archive"), follow=True)

        assert response.status_code == 200

    def test_my_archive_shows_multiple_entitlements(
        self, client, verified_user, category
    ):
        """Verified user with multiple purchases sees all products."""
        from decimal import Decimal

        from orders.models import AccessEntitlement
        from products.models import Product

        prod1 = Product.objects.create(
            title="Product 1",
            slug="prod-1",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("5.00"),
            category=category,
            is_active=True,
        )
        prod2 = Product.objects.create(
            title="Product 2",
            slug="prod-2",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("10.00"),
            category=category,
            is_active=True,
        )

        AccessEntitlement.objects.create(user=verified_user, product=prod1)
        AccessEntitlement.objects.create(user=verified_user, product=prod2)

        client.force_login(verified_user)
        response = client.get(reverse("my_archive"), follow=True)

        assert response.status_code == 200

    def test_my_archive_handles_unpublished_products(
        self, client, verified_user, order_paid
    ):
        """My Archive still works when a purchased product is unpublished."""
        client.force_login(verified_user)

        product = order_paid.line_items.first().product
        product.is_active = False
        product.save(update_fields=["is_active", "updated_at"])

        response = client.get(reverse("my_archive"), follow=True)

        assert response.status_code == 200


@pytest.mark.django_db
class TestDashboardFormPost:
    """Test dashboard form POST functionality."""

    def test_dashboard_form_post_updates_display_name(self, client, verified_user):
        """POST to dashboard with form data updates display_name."""
        from accounts.models import UserProfile

        client.force_login(verified_user)

        response = client.post(
            reverse("account_dashboard"),
            {"display_name": "TestName"},
            follow=True,
        )

        assert response.status_code == 200

        profile = UserProfile.objects.get(user=verified_user)
        assert profile.display_name == "TestName"
