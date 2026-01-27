"""Tests for the reviews app."""

from decimal import Decimal
from typing import Any, cast

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import AccessEntitlement
from products.models import Category, Product
from reviews.models import Review

User = get_user_model()

class ReviewCreationTest(TestCase):
    """Test review creation permissions."""

    def setUp(self):
        """Set up test data."""
        user_model = cast(Any, User)

        self.buyer = user_model.objects.create_user(
            username="buyer",
            email="buyer@test.com",
            password="pass123",
        )
        self.non_buyer = user_model.objects.create_user(
            username="nonbuyer",
            email="nonbuyer@test.com",
            password="pass123",
        )

        EmailAddress.objects.create(
            user=self.buyer,
            email=self.buyer.email,
            verified=True,
            primary=True,
        )
        EmailAddress.objects.create(
            user=self.non_buyer,
            email=self.non_buyer.email,
            verified=True,
            primary=True,
        )

        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category",
        )
        self.product = Product.objects.create(
            title="Test Archive",
            slug="test-archive",
            tagline="Test tagline",
            description="Test description",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test image",
            category=self.category,
        )

        AccessEntitlement.objects.create(
            user=self.buyer,
            product=self.product,
        )

    def test_non_buyer_cannot_see_review_form(self):
        """Non-buyers should not see the review form."""
        self.client.force_login(self.non_buyer)
        response = self.client.get(
            reverse("product_detail", kwargs={"slug": self.product.slug})
        )
        self.assertNotIn(b"Leave a Review", response.content)

    def test_buyer_can_see_review_form(self):
        """Buyers should see the review form."""
        self.client.force_login(self.buyer)
        response = self.client.get(
            reverse("product_detail", kwargs={"slug": self.product.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["can_review"])

    def test_buyer_can_post_review(self):
        """Buyers can successfully submit reviews."""
        self.client.force_login(self.buyer)
        response = self.client.post(
            reverse("create_review", kwargs={"slug": self.product.slug}),
            {
                "rating": 5,
                "title": "Great archive!",
                "body": "Really enjoyed this content.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Review.objects.filter(user=self.buyer, product=self.product).exists()
        )

    def test_non_buyer_cannot_post_review(self):
        """Non-buyers cannot submit reviews."""
        self.client.force_login(self.non_buyer)
        response = self.client.post(
            reverse("create_review", kwargs={"slug": self.product.slug}),
            {
                "rating": 5,
                "title": "Fake review",
                "body": "I did not buy this.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Review.objects.filter(user=self.non_buyer, product=self.product).exists()
        )

    def test_anonymous_cannot_post_review(self):
        """Anonymous users are redirected to login."""
        response = self.client.post(
            reverse("create_review", kwargs={"slug": self.product.slug}),
            {
                "rating": 5,
                "title": "Anonymous review",
                "body": "Cannot post.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

class DashboardReviewsTabTest(TestCase):
    """Test account dashboard reviews tab behavior."""

    def setUp(self):
        """Set up test data."""
        user_model = cast(Any, User)

        self.user = user_model.objects.create_user(
            username="dashreview",
            email="dashreview@test.com",
            password="pass123",
        )
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True,
        )

        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category",
        )

        self.product = Product.objects.create(
            title="Dashboard Review Product",
            slug="dashboard-review-product",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test",
            category=self.category,
        )

        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            title="Dashboard Title",
            body="Dashboard body text",
        )

    def test_my_reviews_redirects_to_dashboard_tab(self):
        """My reviews shortcut redirects to dashboard reviews tab."""
        self.client.force_login(self.user)
        response = self.client.get(reverse("my_reviews"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_dashboard"), response["Location"])
        self.assertIn("tab=reviews", response["Location"])

    def test_dashboard_reviews_tab_renders_for_user(self):
        """Dashboard reviews tab renders and shows the user's review content."""
        self.client.force_login(self.user)
        response = self.client.get(f"{reverse('account_dashboard')}?tab=reviews")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard Title", response.content)
        self.assertIn(b"Dashboard body text", response.content)


class ReviewRemovalTest(TestCase):
    """Test that removed products block review actions."""

    def setUp(self):
        """Set up test data."""
        user_model = cast(Any, User)

        self.buyer = user_model.objects.create_user(
            username="reviewbuyer",
            email="reviewbuyer@test.com",
            password="pass123",
        )
        self.other_buyer = user_model.objects.create_user(
            username="reviewbuyer2",
            email="reviewbuyer2@test.com",
            password="pass123",
        )

        EmailAddress.objects.create(
            user=self.buyer,
            email=self.buyer.email,
            verified=True,
            primary=True,
        )
        EmailAddress.objects.create(
            user=self.other_buyer,
            email=self.other_buyer.email,
            verified=True,
            primary=True,
        )

        self.category = Category.objects.create(
            name="Removed Review Category",
            slug="removed-review-category",
        )
        self.product = Product.objects.create(
            title="Removed Review Product",
            slug="removed-review-product",
            tagline="Test tagline",
            description="Test description",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test image",
            category=self.category,
        )

        AccessEntitlement.objects.create(
            user=self.buyer,
            product=self.product,
        )
        AccessEntitlement.objects.create(
            user=self.other_buyer,
            product=self.product,
        )

        self.review = Review.objects.create(
            user=self.buyer,
            product=self.product,
            rating=5,
            title="Original Review Title",
            body="Original review body.",
        )

    def test_removed_product_blocks_new_review(self):
        """Removed product blocks new review creation."""
        self.product.is_removed = True
        self.product.save()

        self.client.force_login(self.other_buyer)
        response = self.client.post(
            reverse("create_review", kwargs={"slug": self.product.slug}),
            {
                "rating": 4,
                "title": "Blocked Review",
                "body": "Should not be saved.",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            Review.objects.filter(user=self.other_buyer, product=self.product).exists()
        )

    def test_removed_product_blocks_edit_review(self):
        """Removed product blocks review edits."""
        self.product.is_removed = True
        self.product.save()

        self.client.force_login(self.buyer)
        response = self.client.get(
            reverse(
                "edit_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.id},
            )
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.post(
            reverse(
                "edit_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.id},
            ),
            {"rating": 3, "title": "Updated", "body": "Updated body."},
        )
        self.assertEqual(response.status_code, 404)

        self.review.refresh_from_db()
        self.assertEqual(self.review.title, "Original Review Title")

    def test_removed_product_blocks_delete_review(self):
        """Removed product blocks review deletions."""
        self.product.is_removed = True
        self.product.save()

        self.client.force_login(self.buyer)
        response = self.client.post(
            reverse(
                "delete_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.id},
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())
