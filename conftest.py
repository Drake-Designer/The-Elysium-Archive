"""Pytest configuration and fixtures."""

from decimal import Decimal
from typing import Any, cast

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from orders.models import AccessEntitlement, Order
from products.models import Category, Product

User = get_user_model()


def _make_test_password():
    """Generate a non-hardcoded password for test users."""
    return get_random_string(12)


@pytest.fixture
def category():
    """Create a test category."""
    return Category.objects.create(name="Test Category", slug="test-category")


@pytest.fixture
def product_active(category):
    """Create an active test product."""
    return Product.objects.create(
        title="Active Product",
        slug="active-product",
        tagline="A short tagline for testing",
        description="A test product",
        content=(
            "<p>This is the full premium content available after purchase.</p>"
        ),
        price=Decimal("9.99"),
        image_alt="Test image",
        is_active=True,
        category=category,
    )


@pytest.fixture
def product_inactive(category):
    """Create an inactive test product."""
    return Product.objects.create(
        title="Inactive Product",
        slug="inactive-product",
        tagline="A short tagline for testing",
        description="An inactive test product",
        content="<p>This product is inactive for testing purposes.</p>",
        price=Decimal("14.99"),
        image_alt="Test image",
        is_active=False,
        category=category,
    )


@pytest.fixture
def verified_user(db):
    """Create a verified test user."""
    user_model = cast(Any, User)
    user = user_model.objects.create_user(
        username="verified",
        email="verified@test.com",
        password=_make_test_password(),
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=True,
        primary=True,
    )
    return user


@pytest.fixture
def unverified_user(db):
    """Create an unverified test user."""
    user_model = cast(Any, User)
    user = user_model.objects.create_user(
        username="unverified",
        email="unverified@test.com",
        password=_make_test_password(),
    )
    EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True,
    )
    return user


@pytest.fixture
def staff_user(db):
    """Create a staff user."""
    user_model = cast(Any, User)
    return user_model.objects.create_user(
        username="staff",
        email="staff@test.com",
        password=_make_test_password(),
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def client_with_cart(client, product_active):
    """Create a client with items in cart session."""
    session = client.session
    session["cart"] = {str(product_active.id): 1}
    session.save()
    return client


@pytest.fixture
def entitlement(verified_user, product_active):
    """Create an entitlement (purchase) for a user."""
    return AccessEntitlement.objects.create(
        user=cast(Any, verified_user),
        product=product_active,
    )


@pytest.fixture
def order_pending(verified_user, product_active):
    """Create a pending order."""
    order = Order.objects.create(
        user=cast(Any, verified_user),
        total=product_active.price,
        status="pending",
    )

    from orders.models import OrderLineItem

    OrderLineItem.objects.create(
        order=order,
        product=product_active,
        product_title=product_active.title,
        product_price=product_active.price,
        quantity=1,
        line_total=product_active.price,
    )
    return order


@pytest.fixture
def order_paid(verified_user, product_active):
    """Create a paid order with entitlement."""
    order = Order.objects.create(
        user=cast(Any, verified_user),
        total=product_active.price,
        status="paid",
    )

    from orders.models import OrderLineItem

    OrderLineItem.objects.create(
        order=order,
        product=product_active,
        product_title=product_active.title,
        product_price=product_active.price,
        quantity=1,
        line_total=product_active.price,
    )

    AccessEntitlement.objects.create(
        user=cast(Any, verified_user),
        product=product_active,
        order=order,
    )
    return order
