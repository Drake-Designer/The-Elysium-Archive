"""Pytest configuration and shared test fixtures for all apps."""

import os
import pytest
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from products.models import Product, Category
from orders.models import Order, OrderLineItem, AccessEntitlement


@pytest.fixture(autouse=True)
def disable_staticfiles(settings):
    """Disable WhiteNoise staticfiles storage for tests."""
    settings.STATICFILES_STORAGE = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    # Remove WhiteNoise from middleware
    settings.MIDDLEWARE = [
        m for m in settings.MIDDLEWARE if "whitenoise" not in m.lower()
    ]


User = get_user_model()


@pytest.fixture
def verified_user(db):
    """Create a user with verified email."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
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
    """Create a user without verified email."""
    user = User.objects.create_user(
        username="unverified",
        email="unverified@example.com",
        password="testpass123",
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
    """Create a staff/superuser."""
    return User.objects.create_superuser(
        username="staffuser",
        email="staff@example.com",
        password="testpass123",
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name="Test Category",
        slug="test-category",
    )


@pytest.fixture
def product_active(db, category):
    """Create an active product."""
    return Product.objects.create(
        title="Active Product",
        slug="active-product",
        description="A test product",
        tagline="Test tagline for product",
        content="This is the full archive content that should only appear on the reading page.",
        price=Decimal("9.99"),
        category=category,
        is_active=True,
        is_featured=False,
    )


@pytest.fixture
def product_inactive(db, category):
    """Create an inactive (unpublished) product."""
    return Product.objects.create(
        title="Inactive Product",
        slug="inactive-product",
        description="A test product",
        price=Decimal("19.99"),
        category=category,
        is_active=False,
        is_featured=False,
    )


@pytest.fixture
def entitlement(db, verified_user, product_active):
    """Create an AccessEntitlement for a user."""
    return AccessEntitlement.objects.create(
        user=verified_user,
        product=product_active,
    )


@pytest.fixture
def order_pending(db, verified_user, product_active):
    """Create a pending order with line items."""
    order = Order.objects.create(
        user=verified_user,
        status="pending",
        total=Decimal("9.99"),
    )
    OrderLineItem.objects.create(
        order=order,
        product=product_active,
        product_title=product_active.title,
        product_price=product_active.price,
        quantity=1,
    )
    return order


@pytest.fixture
def order_paid(db, verified_user, product_active):
    """Create a paid order (with entitlements already granted)."""
    order = Order.objects.create(
        user=verified_user,
        status="paid",
        total=Decimal("9.99"),
        stripe_session_id="cs_test123",
        stripe_pid="pi_test123",
    )
    OrderLineItem.objects.create(
        order=order,
        product=product_active,
        product_title=product_active.title,
        product_price=product_active.price,
        quantity=1,
    )
    # Create entitlement (as if webhook already ran)
    AccessEntitlement.objects.create(
        user=verified_user,
        product=product_active,
        order=order,
    )
    return order


@pytest.fixture
def client_with_cart(client, verified_user):
    """Provide a client with a user session that has a cart."""
    client.force_login(verified_user)
    return client
