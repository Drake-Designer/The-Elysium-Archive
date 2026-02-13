"""Tests for deal banner admin behavior and sync rules."""

from decimal import Decimal

import pytest
from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from products.admin import DealBannerAdmin
from products.models import Category, DealBanner, Product


def _create_product(
    *, category, title, slug, is_active=True, is_removed=False
):
    """Create a product for deal banner tests."""
    return Product.objects.create(
        title=title,
        slug=slug,
        tagline="Test tagline",
        description="Test description",
        content="<p>Test premium content.</p>",
        price=Decimal("9.99"),
        image_alt="Test image",
        category=category,
        is_active=is_active,
        is_removed=is_removed,
    )


@pytest.mark.django_db
class TestDealBannerAdminActions:
    """Test admin controls for activating and deactivating banners."""

    def test_staff_can_mark_selected_banners_active(
        self, client, staff_user, product_active
    ):
        """Staff can activate selected deal banners in bulk."""
        banner_one = DealBanner.objects.create(
            title="ONE",
            message="First",
            product=product_active,
            is_active=False,
            order=0,
        )
        banner_two = DealBanner.objects.create(
            title="TWO",
            message="Second",
            is_active=False,
            order=1,
        )

        client.force_login(staff_user)
        response = client.post(
            reverse("admin:products_dealbanner_changelist"),
            {
                "action": "mark_selected_deal_banners_active",
                "_selected_action": [str(banner_one.pk), str(banner_two.pk)],
                "index": "0",
                "select_across": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        banner_one.refresh_from_db()
        banner_two.refresh_from_db()
        product_active.refresh_from_db()

        assert banner_one.is_active is True
        assert banner_two.is_active is True
        assert product_active.is_deal is True

    def test_staff_can_mark_selected_banners_inactive(
        self, client, staff_user, product_active
    ):
        """Staff can deactivate selected deal banners in bulk."""
        banner = DealBanner.objects.create(
            title="DEAL",
            message="Product deal",
            product=product_active,
            is_active=True,
            order=0,
        )
        product_active.refresh_from_db()
        assert product_active.is_deal is True

        client.force_login(staff_user)
        response = client.post(
            reverse("admin:products_dealbanner_changelist"),
            {
                "action": "mark_selected_deal_banners_inactive",
                "_selected_action": [str(banner.pk)],
                "index": "0",
                "select_across": "0",
            },
            follow=True,
        )

        assert response.status_code == 200
        banner.refresh_from_db()
        product_active.refresh_from_db()

        assert banner.is_active is False
        assert product_active.is_deal is False

    def test_regular_user_cannot_run_deal_banner_actions(
        self, client, verified_user
    ):
        """Regular user cannot access deal banner admin actions."""
        banner = DealBanner.objects.create(
            title="DEAL",
            message="Locked",
            is_active=False,
            order=0,
        )

        client.force_login(verified_user)
        response = client.post(
            reverse("admin:products_dealbanner_changelist"),
            {
                "action": "mark_selected_deal_banners_active",
                "_selected_action": [str(banner.pk)],
                "index": "0",
                "select_across": "0",
            },
            follow=False,
        )

        assert response.status_code in [302, 403]
        banner.refresh_from_db()
        assert banner.is_active is False

    def test_staff_can_toggle_is_active_from_changelist_inline(
        self, client, staff_user
    ):
        """Staff can toggle is_active through list editable form."""
        banner = DealBanner.objects.create(
            title="INLINE",
            message="Inline toggle",
            is_active=False,
            order=0,
        )

        client.force_login(staff_user)
        changelist_url = reverse("admin:products_dealbanner_changelist")

        activate_response = client.post(
            changelist_url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(banner.pk),
                "form-0-order": "0",
                "form-0-is_active": "on",
                "_save": "Save",
            },
            follow=True,
        )
        assert activate_response.status_code == 200
        banner.refresh_from_db()
        assert banner.is_active is True

        deactivate_response = client.post(
            changelist_url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": str(banner.pk),
                "form-0-order": "0",
                "_save": "Save",
            },
            follow=True,
        )
        assert deactivate_response.status_code == 200
        banner.refresh_from_db()
        assert banner.is_active is False


@pytest.mark.django_db
class TestDealBannerDestinationPriority:
    """Test destination resolution shown in admin."""

    def test_destination_display_uses_effective_destination_priority(
        self, category
    ):
        """Admin destination label matches the effective URL priority."""
        product = _create_product(
            category=category,
            title="Priority Product",
            slug="priority-product",
            is_active=True,
        )
        banner = DealBanner.objects.create(
            title="PRIORITY",
            message="Priority destination",
            product=product,
            category=category,
            url="https://example.com/custom",
            is_active=True,
            order=0,
        )

        admin_instance = DealBannerAdmin(DealBanner, AdminSite())
        html_when_active = str(admin_instance.destination_display(banner))

        assert banner.get_url() == product.get_absolute_url()
        assert "Product" in html_when_active
        assert product.title in html_when_active
        assert product.get_absolute_url() in html_when_active

        product.is_active = False
        product.save(update_fields=["is_active", "updated_at"])
        banner.refresh_from_db()

        html_when_inactive = str(admin_instance.destination_display(banner))

        assert banner.get_url() == "https://example.com/custom"
        assert "Custom URL" in html_when_inactive
        assert "https://example.com/custom" in html_when_inactive


@pytest.mark.django_db
class TestDealBannerSync:
    """Test deal sync behavior for product and category targets."""

    def test_product_banner_create_deactivate_delete_syncs_deal_status(
        self, product_active
    ):
        """Product deal status updates on create, deactivate, and delete."""
        banner = DealBanner.objects.create(
            title="PRODUCT",
            message="Product deal",
            product=product_active,
            is_active=True,
            order=0,
        )
        product_active.refresh_from_db()
        assert product_active.is_deal is True

        banner.is_active = False
        banner.save(update_fields=["is_active"])
        product_active.refresh_from_db()
        assert product_active.is_deal is False

        banner.is_active = True
        banner.save(update_fields=["is_active"])
        product_active.refresh_from_db()
        assert product_active.is_deal is True

        banner.delete()
        product_active.refresh_from_db()
        assert product_active.is_deal is False

    def test_reassigning_product_banner_resyncs_old_and_new_products(
        self, category
    ):
        """Changing a banner product clears old target and sets new target."""
        product_one = _create_product(
            category=category,
            title="Product One",
            slug="product-one",
            is_active=True,
        )
        product_two = _create_product(
            category=category,
            title="Product Two",
            slug="product-two",
            is_active=True,
        )

        banner = DealBanner.objects.create(
            title="SWAP",
            message="Swap product target",
            product=product_one,
            is_active=True,
            order=0,
        )
        product_one.refresh_from_db()
        product_two.refresh_from_db()
        assert product_one.is_deal is True
        assert product_two.is_deal is False

        banner.product = product_two
        banner.save(update_fields=["product"])

        product_one.refresh_from_db()
        product_two.refresh_from_db()
        assert product_one.is_deal is False
        assert product_two.is_deal is True

    def test_reassigning_category_banner_resyncs_old_and_new_categories(self):
        """Changing a banner category clears old category deals."""
        category_one = Category.objects.create(
            name="Category One",
            slug="category-one",
        )
        category_two = Category.objects.create(
            name="Category Two",
            slug="category-two",
        )
        product_one = _create_product(
            category=category_one,
            title="Category Product One",
            slug="category-product-one",
            is_active=True,
        )
        product_two = _create_product(
            category=category_two,
            title="Category Product Two",
            slug="category-product-two",
            is_active=True,
        )

        banner = DealBanner.objects.create(
            title="CATEGORY",
            message="Category deal",
            category=category_one,
            is_active=True,
            order=0,
        )
        product_one.refresh_from_db()
        product_two.refresh_from_db()
        assert product_one.is_deal is True
        assert product_two.is_deal is False

        banner.category = category_two
        banner.save(update_fields=["category"])

        product_one.refresh_from_db()
        product_two.refresh_from_db()
        assert product_one.is_deal is False
        assert product_two.is_deal is True

    def test_category_banner_marks_only_active_non_removed_products(self):
        """Category banner applies deal status only to active products."""
        category = Category.objects.create(
            name="Active Only Category",
            slug="active-only-category",
        )
        active_product = _create_product(
            category=category,
            title="Active Deal",
            slug="active-deal",
            is_active=True,
        )
        inactive_product = _create_product(
            category=category,
            title="Inactive Deal",
            slug="inactive-deal",
            is_active=False,
        )
        removed_product = _create_product(
            category=category,
            title="Removed Deal",
            slug="removed-deal",
            is_active=False,
            is_removed=True,
        )

        Product.objects.filter(pk=inactive_product.pk).update(is_deal=True)
        Product.objects.filter(pk=removed_product.pk).update(is_deal=True)

        DealBanner.objects.create(
            title="CATEGORY ACTIVE",
            message="Category active only",
            category=category,
            is_active=True,
            order=0,
        )

        active_product.refresh_from_db()
        inactive_product.refresh_from_db()
        removed_product.refresh_from_db()

        assert active_product.is_deal is True
        assert inactive_product.is_deal is False
        assert removed_product.is_deal is False

    def test_product_deactivation_resyncs_deal_status_with_active_only_rule(
        self, product_active
    ):
        """Product loses deal status when it becomes inactive."""
        DealBanner.objects.create(
            title="ACTIVE ONLY",
            message="Active product deal",
            product=product_active,
            is_active=True,
            order=0,
        )
        product_active.refresh_from_db()
        assert product_active.is_deal is True

        product_active.is_active = False
        product_active.save(update_fields=["is_active", "updated_at"])
        product_active.refresh_from_db()

        assert product_active.is_deal is False
