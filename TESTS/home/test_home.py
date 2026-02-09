"""Tests for admin protection rules and deal banner visibility."""

import pytest
from django.urls import reverse

from products.models import Product


@pytest.mark.django_db
class TestAdminAccess:
    """Test admin panel access control."""

    def test_anonymous_cannot_access_admin(self, client):
        """Anonymous user is redirected away from Django admin."""
        response = client.get(reverse("admin:index"), follow=False)

        assert response.status_code == 302
        assert (
            reverse("admin:login") in response.url or "login" in response.url
        )

    def test_regular_user_cannot_access_admin(self, client, verified_user):
        """Regular (non-staff) user cannot access admin."""
        client.force_login(verified_user)
        response = client.get(reverse("admin:index"), follow=False)

        assert response.status_code in [302, 403]

    def test_staff_can_access_admin(self, client, staff_user):
        """Staff user can access Django admin."""
        client.force_login(staff_user)
        response = client.get(reverse("admin:index"))

        assert response.status_code == 200


@pytest.mark.django_db
class TestAdminProductDelete:
    """Test product unpublish behavior when delete is used in admin."""

    def test_admin_delete_unpublishes_product(
        self, client, staff_user, product_active
    ):
        """Admin delete converts to unpublish and keeps product in database."""
        client.force_login(staff_user)

        response = client.post(
            reverse("admin:products_product_delete", args=[product_active.pk]),
            {"post": "yes"},
            follow=True,
        )

        assert response.status_code == 200

        product_active.refresh_from_db()
        assert product_active.is_active is False
        assert Product.objects.filter(pk=product_active.pk).exists() is True

    def test_bulk_delete_unpublishes_products(
        self, client, staff_user, category
    ):
        """Bulk delete converts to unpublish for all selected products."""
        from decimal import Decimal

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

        client.force_login(staff_user)

        response = client.post(
            reverse("admin:products_product_changelist"),
            {
                "action": "unpublish_products",
                "_selected_action": [str(prod1.pk), str(prod2.pk)],
            },
            follow=True,
        )

        assert response.status_code == 200

        prod1.refresh_from_db()
        prod2.refresh_from_db()
        assert prod1.is_active is False
        assert prod2.is_active is False


@pytest.mark.django_db
class TestAdminFeaturedToggle:
    """Test featured toggle action in admin."""

    def test_staff_can_toggle_featured(
        self, client, staff_user, product_active
    ):
        """Staff user can toggle product featured status using change form."""
        client.force_login(staff_user)

        assert product_active.is_featured is False

        response = client.post(
            reverse("admin:products_product_change", args=[product_active.pk]),
            {
                "title": product_active.title,
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": product_active.description,
                "price": str(product_active.price),
                "image_alt": product_active.image_alt,
                "category": product_active.category.pk,
                "content": product_active.content,
                "is_active": "on",
                "is_featured": "on",
            },
            follow=True,
        )

        assert response.status_code == 200
        product_active.refresh_from_db()
        assert product_active.is_featured is True

        response = client.post(
            reverse("admin:products_product_change", args=[product_active.pk]),
            {
                "title": product_active.title,
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": product_active.description,
                "price": str(product_active.price),
                "image_alt": product_active.image_alt,
                "category": product_active.category.pk,
                "content": product_active.content,
                "is_active": "on",
            },
            follow=True,
        )

        assert response.status_code == 200
        product_active.refresh_from_db()
        assert product_active.is_featured is False

    def test_regular_user_cannot_toggle_featured(
        self,
        client,
        verified_user,
        product_active,
    ):
        """Regular user cannot access product admin change list."""
        client.force_login(verified_user)

        response = client.get(
            reverse("admin:products_product_changelist"),
            follow=False,
        )

        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestAdminProductForm:
    """Test admin product form validation and basic edits."""

    def test_staff_can_edit_product(self, client, staff_user, product_active):
        """Staff can edit product details in admin."""
        client.force_login(staff_user)

        response = client.post(
            reverse("admin:products_product_change", args=[product_active.pk]),
            {
                "title": "Updated Title",
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": "Updated description",
                "content": product_active.content,
                "price": "9.99",
                "image_alt": "Updated alt text",
                "category": product_active.category.pk,
                "is_active": "on",
            },
            follow=True,
        )

        assert response.status_code == 200
        product_active.refresh_from_db()
        assert product_active.title == "Updated Title"

    def test_staff_can_deactivate_product(
        self, client, staff_user, product_active
    ):
        """Staff can set is_active to False via admin form."""
        client.force_login(staff_user)

        response = client.post(
            reverse("admin:products_product_change", args=[product_active.pk]),
            {
                "title": product_active.title,
                "slug": product_active.slug,
                "tagline": product_active.tagline,
                "description": product_active.description,
                "content": product_active.content,
                "price": str(product_active.price),
                "image_alt": "Alt text",
                "category": product_active.category.pk,
            },
            follow=True,
        )

        assert response.status_code == 200
        product_active.refresh_from_db()
        assert product_active.is_active is False


@pytest.mark.django_db
class TestAdminOrderAccess:
    """Test admin order visibility and access control."""

    def test_staff_can_view_orders(self, client, staff_user, order_pending):
        """Staff can view order list in admin."""
        client.force_login(staff_user)

        response = client.get(reverse("admin:orders_order_changelist"))

        assert response.status_code == 200

    def test_staff_can_view_order_detail(
        self, client, staff_user, order_pending
    ):
        """Staff can view order details in admin."""
        client.force_login(staff_user)

        response = client.get(
            reverse("admin:orders_order_change", args=[order_pending.pk])
        )

        assert response.status_code == 200

    def test_regular_user_cannot_view_orders(self, client, verified_user):
        """Regular user cannot access order admin pages."""
        client.force_login(verified_user)

        response = client.get(
            reverse("admin:orders_order_changelist"),
            follow=False,
        )

        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestDealBannerVisibilityRules:
    """Test DealBanner display and link rules on the homepage."""

    def test_product_link_banner_hidden_when_unpublished_and_no_fallbacks(
        self,
        client,
        product_active,
    ):
        """
        Product banner is hidden if linked product is inactive and no URL or
        category fallback exists.
        """
        from products.models import DealBanner

        banner = DealBanner.objects.create(
            title="DEAL",
            message="Single product deal",
            product=product_active,
            is_active=True,
            order=0,
        )

        product_active.is_active = False
        product_active.save(update_fields=["is_active", "updated_at"])

        response = client.get(reverse("home"))
        assert response.status_code == 200

        html = response.content.decode()
        assert banner.message not in html

    def test_product_link_banner_kept_when_url_exists(
        self,
        client,
        product_active,
    ):
        """
        If product is inactive but banner has URL, banner stays and links to
        URL instead of product.
        """

        from products.models import DealBanner

        banner = DealBanner.objects.create(
            title="DEAL",
            message="Fallback url deal",
            product=product_active,
            url="https://example.com/fallback",
            is_active=True,
            order=0,
        )

        product_active.is_active = False
        product_active.save(update_fields=["is_active", "updated_at"])

        response = client.get(reverse("home"))
        assert response.status_code == 200

        html = response.content.decode()
        assert banner.message in html
        assert "example.com/fallback" in html
        assert product_active.get_absolute_url() not in html

    def test_category_banner_hidden_if_category_has_no_active_products(
        self,
        client,
        category,
    ):
        """
        Category banner is hidden when all products in that category are
        inactive.
        """

        from decimal import Decimal

        from products.models import DealBanner, Product

        prod1 = Product.objects.create(
            title="CatProd1",
            slug="catprod1",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("5.00"),
            category=category,
            is_active=False,
        )
        prod2 = Product.objects.create(
            title="CatProd2",
            slug="catprod2",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("10.00"),
            category=category,
            is_active=False,
        )

        banner = DealBanner.objects.create(
            title="DEAL",
            message="Category deal",
            category=category,
            is_active=True,
            order=0,
        )

        response = client.get(reverse("home"))
        assert response.status_code == 200

        html = response.content.decode()
        assert banner.message not in html
        assert prod1.get_absolute_url() not in html
        assert prod2.get_absolute_url() not in html

    def test_category_banner_shown_when_category_has_active_products(
        self,
        client,
        category,
    ):
        """
        Category banner shows and links to archive with category and deals
        filter when at least one active product exists.
        """

        from decimal import Decimal

        from products.models import DealBanner, Product

        Product.objects.create(
            title="CatProdActive",
            slug="catprodactive",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("5.00"),
            category=category,
            is_active=True,
        )

        banner = DealBanner.objects.create(
            title="DEAL",
            message="Category deal active",
            category=category,
            is_active=True,
            order=0,
        )

        response = client.get(reverse("home"))
        assert response.status_code == 200

        html = response.content.decode()
        assert banner.message in html
        assert f"cat={category.slug}" in html
        assert "deals=true" in html

    def test_global_deals_banner_hidden_when_no_active_deal_products(
        self, client
    ):
        """
        Global deals banner is hidden if there are no active deal
        products.
        """

        from products.models import DealBanner

        banner = DealBanner.objects.create(
            title="DEAL",
            message="All deals",
            is_active=True,
            order=0,
        )

        response = client.get(reverse("home"))
        assert response.status_code == 200

        html = response.content.decode()
        assert banner.message not in html

    def test_global_deals_banner_shown_when_active_deal_products_exist(
        self,
        client,
        product_active,
    ):
        """
        Global deals banner is hidden if there are no active deal products.
        """

        from products.models import DealBanner

        # Create a global banner (no product, no category)
        banner = DealBanner.objects.create(
            title="DEAL",
            message="All deals visible",
            is_active=True,
            order=0,
        )

        # Mark product as a deal so that the global banner is relevant
        product_active.is_deal = True
        product_active.save(update_fields=["is_deal", "updated_at"])

        response = client.get(reverse("home"))
        assert response.status_code == 200

        html = response.content.decode()
        assert banner.message in html
        assert "?deals=true" in html
