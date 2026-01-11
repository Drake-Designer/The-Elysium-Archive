"""Tests for archive reading page access control and content separation."""

import pytest
from django.urls import reverse
from orders.models import AccessEntitlement


@pytest.mark.django_db
class TestArchiveReadAccess:
    """Test access control for the archive reading page."""

    def test_anonymous_user_redirected_to_login(self, client, product_active):
        """Anonymous user is redirected to login page."""
        response = client.get(reverse("archive_read", args=[product_active.slug]))

        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_authenticated_user_without_entitlement_denied(
        self, client, verified_user, product_active
    ):
        """Authenticated user without entitlement receives 403."""
        client.force_login(verified_user)
        response = client.get(reverse("archive_read", args=[product_active.slug]))

        assert response.status_code == 403

    def test_owner_can_access_reading_page(self, client, verified_user, product_active):
        """User with entitlement can access reading page."""
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(verified_user)
        response = client.get(reverse("archive_read", args=[product_active.slug]))

        assert response.status_code == 200

    def test_reading_page_displays_full_content(
        self, client, verified_user, product_active
    ):
        """Reading page displays the full archive content."""
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(verified_user)
        response = client.get(reverse("archive_read", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()
        # Full content should be present
        assert product_active.content in content or "Complete Archive Entry" in content

    def test_unverified_email_redirected_to_verification(
        self, client, unverified_user, product_active
    ):
        """User with unverified email is redirected to email verification."""
        AccessEntitlement.objects.create(user=unverified_user, product=product_active)

        client.force_login(unverified_user)
        response = client.get(reverse("archive_read", args=[product_active.slug]))

        assert response.status_code == 302
        assert "/accounts/email/" in response.url


@pytest.mark.django_db
class TestPreviewPageContentSeparation:
    """Test that preview page never displays full content."""

    def test_preview_page_does_not_show_full_content_for_owner(
        self, client, verified_user, product_active
    ):
        """Preview page does not show full content even for owners."""
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(verified_user)
        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()

        # Full content should NOT be present on preview page
        assert product_active.content not in content

        # Button to reading page should be present
        assert "Read Full Archive" in content
        assert "archive_read" in content or f"{product_active.slug}/read/" in content

    def test_preview_page_shows_read_button_for_owner(
        self, client, verified_user, product_active
    ):
        """Preview page shows 'Read Full Archive' button for owners."""
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(verified_user)
        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()

        # Check for button presence
        assert "Read Full Archive" in content
        # Check that button links to reading page, not anchor
        assert "#full-content" not in content or "archive_read" in content

    def test_preview_page_does_not_show_full_content_for_non_owner(
        self, client, verified_user, product_active
    ):
        """Preview page does not show full content for non-owners."""
        client.force_login(verified_user)
        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()

        # Full content should NOT be present
        assert product_active.content not in content

        # Purchase CTA should be present
        assert "Add to Cart" in content or "Proceed to Checkout" in content

    def test_anonymous_preview_does_not_show_full_content(self, client, product_active):
        """Anonymous users cannot see full content on preview page."""
        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()

        # Full content should NOT be present
        assert product_active.content not in content


@pytest.mark.django_db
class TestMyArchiveNavigation:
    """Test that My Archive links to reading page."""

    def test_my_archive_links_to_reading_page(
        self, client, verified_user, product_active
    ):
        """My Archive page links to archive_read, not product_detail."""
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(verified_user)
        response = client.get(reverse("my_archive"), follow=True)

        assert response.status_code == 200
        content = response.content.decode()

        # Should link to reading page
        assert "archive_read" in content or f"{product_active.slug}/read/" in content

        # Product title should be present
        assert product_active.title in content


@pytest.mark.django_db
class TestReadingPageNavigation:
    """Test navigation elements on reading page."""

    def test_reading_page_has_back_to_my_archive(
        self, client, verified_user, product_active
    ):
        """Reading page includes link back to My Archive."""
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(verified_user)
        response = client.get(reverse("archive_read", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()

        # Check for navigation
        assert "My Archive" in content
        assert "/accounts/archive/" in content or "my_archive" in content.lower()

    def test_reading_page_has_link_to_preview(
        self, client, verified_user, product_active
    ):
        """Reading page includes link to product detail page."""
        AccessEntitlement.objects.create(user=verified_user, product=product_active)

        client.force_login(verified_user)
        response = client.get(reverse("archive_read", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()

        # Check for link to detail page
        assert "View Details" in content or "product_detail" in content
