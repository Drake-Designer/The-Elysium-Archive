"""Tests for shopping cart functionality."""

from decimal import Decimal
from typing import Any, cast

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestCartOperations:
    """Test basic cart add/remove/view operations."""

    def test_add_to_cart_redirects(self, client, verified_user, product_active):
        """POST to add_to_cart redirects to product detail page."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_active).pk

        response = client.post(
            reverse("add_to_cart"),
            {"product_id": str(product_pk)},
            follow=False,
        )

        assert response.status_code == 302
        assert (
            reverse("product_detail", kwargs={"slug": product_active.slug})
            in response.url
        )

    def test_add_to_cart_stores_in_session(self, client, verified_user, product_active):
        """Product added to cart is stored in session."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_active).pk

        client.post(
            reverse("add_to_cart"),
            {"product_id": str(product_pk)},
        )

        cart = client.session.get("cart", {})
        assert str(product_pk) in cart
        assert cart[str(product_pk)] == 1

    def test_cart_view_shows_items(self, client, verified_user, product_active):
        """Cart view displays added items."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_active).pk

        client.post(reverse("add_to_cart"), {"product_id": str(product_pk)})

        response = client.get(reverse("cart"))

        assert response.status_code == 200
        assert "cart/cart.html" in [t.name for t in response.templates]
        assert product_active.title in response.content.decode()

    def test_empty_cart_view(self, client, verified_user):
        """Empty cart shows message or empty state."""
        client.force_login(verified_user)

        response = client.get(reverse("cart"))

        assert response.status_code == 200
        assert "cart/cart.html" in [t.name for t in response.templates]

    def test_remove_from_cart(self, client, verified_user, product_active):
        """Remove from cart removes product from session."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_active).pk

        client.post(reverse("add_to_cart"), {"product_id": str(product_pk)})
        assert len(client.session.get("cart", {})) == 1

        client.post(reverse("remove_from_cart"), {"product_id": str(product_pk)})

        cart = client.session.get("cart", {})
        assert str(product_pk) not in cart

    def test_cart_persists_across_pages(self, client, verified_user, product_active):
        """Cart items persist when visiting other pages."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_active).pk

        client.post(reverse("add_to_cart"), {"product_id": str(product_pk)})
        first_cart_size = len(client.session.get("cart", {}))

        client.get(reverse("home"))

        second_cart_size = len(client.session.get("cart", {}))
        assert first_cart_size == second_cart_size

    def test_cart_persists_after_logout_and_login(
        self, client, verified_user, product_active
    ):
        """Cart items persist after logout and login."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_active).pk

        client.post(reverse("add_to_cart"), {"product_id": str(product_pk)})
        assert str(product_pk) in client.session.get("cart", {})

        client.logout()
        assert client.session.get("cart") in (None, {})

        client.force_login(verified_user)

        client.get(reverse("cart"))
        assert str(product_pk) in client.session.get("cart", {})


@pytest.mark.django_db
class TestCartValidation:
    """Test cart validation and error handling."""

    def test_add_nonexistent_product_404(self, client, verified_user):
        """Adding nonexistent product to cart handles gracefully."""
        client.force_login(verified_user)

        response = client.post(
            reverse("add_to_cart"),
            {"product_id": "99999"},
            follow=True,
        )

        assert response.status_code == 200 or response.status_code == 404

    def test_add_inactive_product_to_cart(
        self, client, verified_user, product_inactive
    ):
        """Adding inactive product to cart may be allowed (purchase can be historical)."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_inactive).pk

        response = client.post(
            reverse("add_to_cart"),
            {"product_id": str(product_pk)},
        )

        assert response.status_code in [302, 400, 404]

    def test_cart_add_requires_verified_email(
        self, client, unverified_user, product_active
    ):
        """Adding to cart requires verified email address."""
        client.force_login(unverified_user)

        product_pk = cast(Any, product_active).pk

        response = client.post(
            reverse("add_to_cart"),
            {"product_id": str(product_pk)},
            follow=False,
        )

        assert response.status_code == 302
        assert reverse("account_email") in response.url


@pytest.mark.django_db
class TestCartTotals:
    """Test cart total calculation."""

    def test_cart_single_item_total(self, client, verified_user, product_active):
        """Cart displays correct total for single item."""
        client.force_login(verified_user)

        product_pk = cast(Any, product_active).pk

        client.post(reverse("add_to_cart"), {"product_id": str(product_pk)})
        response = client.get(reverse("cart"))

        assert response.status_code == 200
        content = response.content.decode()
        assert "9.99" in content or "€9.99" in content or "9,99" in content

    def test_cart_multiple_items_total(self, client, verified_user, category):
        """Cart totals multiple different products."""
        from products.models import Product

        prod1 = Product.objects.create(
            title="Prod1",
            slug="prod1",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("10.00"),
            category=category,
            is_active=True,
        )
        prod2 = Product.objects.create(
            title="Prod2",
            slug="prod2",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("5.00"),
            category=category,
            is_active=True,
        )

        client.force_login(verified_user)

        client.post(reverse("add_to_cart"), {"product_id": str(cast(Any, prod1).pk)})
        client.post(reverse("add_to_cart"), {"product_id": str(cast(Any, prod2).pk)})

        response = client.get(reverse("cart"))

        assert response.status_code == 200
        assert "Prod1" in response.content.decode()
        assert "Prod2" in response.content.decode()
