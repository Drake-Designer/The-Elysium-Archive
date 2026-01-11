"""Tests for the reviews app."""

from decimal import Decimal

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
        self.buyer = User.objects.create_user(
            username="buyer", email="buyer@test.com", password="pass123"
        )
        self.non_buyer = User.objects.create_user(
            username="nonbuyer", email="nonbuyer@test.com", password="pass123"
        )
        
        # Verify emails for both users
        EmailAddress.objects.create(
            user=self.buyer, email=self.buyer.email, verified=True, primary=True
        )
        EmailAddress.objects.create(
            user=self.non_buyer, email=self.non_buyer.email, verified=True, primary=True
        )
        
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
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
        
        # Grant entitlement to buyer
        AccessEntitlement.objects.create(user=self.buyer, product=self.product)

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
        """Non-buyers cannot submit reviews - redirected with error."""
        self.client.force_login(self.non_buyer)
        response = self.client.post(
            reverse("create_review", kwargs={"slug": self.product.slug}),
            {
                "rating": 5,
                "title": "Fake review",
                "body": "I did not buy this.",
            },
        )
        # View redirects with error message, not 403
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


class ReviewDuplicatePreventionTest(TestCase):
    """Test that users can only submit one review per product."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        
        # Verify email
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )
        
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        
        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test",
            category=self.category,
        )
        
        AccessEntitlement.objects.create(user=self.user, product=self.product)
        
        # Create first review
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            title="First review",
            body="Great product",
        )

    def test_user_cannot_post_duplicate_review(self):
        """Users cannot submit multiple reviews for same product."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("create_review", kwargs={"slug": self.product.slug}),
            {
                "rating": 4,
                "title": "Second review",
                "body": "Still great",
            },
        )
        # Should redirect with message
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(user=self.user).count(), 1)


class ReviewDisplayTest(TestCase):
    """Test review display on product pages."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="reviewer", email="reviewer@test.com", password="pass123"
        )
        
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        
        self.product = Product.objects.create(
            title="Product with Reviews",
            slug="product-reviews",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("14.99"),
            image_alt="Test",
            category=self.category,
        )
        
        self.review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            title="Excellent!",
            body="Highly recommended.",
        )

    def test_review_appears_on_product_detail(self):
        """Reviews should be visible on product detail page."""
        response = self.client.get(
            reverse("product_detail", kwargs={"slug": self.product.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Excellent!", response.content)
        self.assertIn(b"Highly recommended.", response.content)

    def test_multiple_reviews_on_product(self):
        """Multiple reviews should all be visible."""
        user2 = User.objects.create_user(
            username="reviewer2", email="reviewer2@test.com", password="pass123"
        )
        Review.objects.create(
            user=user2,
            product=self.product,
            rating=4,
            title="Good",
            body="Pretty good overall.",
        )
        
        response = self.client.get(
            reverse("product_detail", kwargs={"slug": self.product.slug})
        )
        self.assertIn(b"Excellent!", response.content)
        self.assertIn(b"Good", response.content)


class ReviewRatingTest(TestCase):
    """Test review rating validation."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="rater", email="rater@test.com", password="pass123"
        )
        
        # Verify email
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )
        
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        
        self.product = Product.objects.create(
            title="Rated Product",
            slug="rated-product",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test",
            category=self.category,
        )
        AccessEntitlement.objects.create(user=self.user, product=self.product)

    def test_review_rating_valid_range(self):
        """Rating must be between 1 and 5."""
        self.client.force_login(self.user)
        
        # Valid ratings
        for rating in [1, 2, 3, 4, 5]:
            Review.objects.all().delete()
            response = self.client.post(
                reverse("create_review", kwargs={"slug": self.product.slug}),
                {"rating": rating, "title": "Test", "body": "Test body"},
            )
            self.assertEqual(response.status_code, 302)

    def test_review_optional_title(self):
        """Review title should be optional."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("create_review", kwargs={"slug": self.product.slug}),
            {"rating": 5, "title": "", "body": "Just a body"},
        )
        self.assertEqual(response.status_code, 302)


class ReviewModelTest(TestCase):
    """Test Review model behavior."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="modeltest", email="modeltest@test.com", password="pass123"
        )
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        self.product = Product.objects.create(
            title="Model Test Product",
            slug="model-test",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test",
            category=self.category,
        )

    def test_review_str(self):
        """Review __str__ should return readable format."""
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            title="Test Review",
            body="Test body",
        )
        # Match actual __str__ format from models.py
        expected = f"{self.user} reviewed {self.product}"
        self.assertEqual(str(review), expected)

    def test_review_deleted_with_user(self):
        """Reviews should be deleted when user is deleted."""
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            body="Will be deleted",
        )
        self.user.delete()
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_review_deleted_with_product(self):
        """Reviews should be deleted when product is deleted."""
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            body="Will be deleted",
        )
        self.product.delete()
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())


class ReviewEditTest(TestCase):
    """Test review editing functionality."""

    def setUp(self):
        """Set up test data."""
        self.owner = User.objects.create_user(
            username="owner", email="owner@test.com", password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="other", email="other@test.com", password="pass123"
        )
        
        # Verify emails
        EmailAddress.objects.create(
            user=self.owner, email=self.owner.email, verified=True, primary=True
        )
        EmailAddress.objects.create(
            user=self.other_user, email=self.other_user.email, verified=True, primary=True
        )
        
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        
        self.product = Product.objects.create(
            title="Edit Test",
            slug="edit-test",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test",
            category=self.category,
        )
        self.review = Review.objects.create(
            user=self.owner,
            product=self.product,
            rating=5,
            title="Original",
            body="Original body",
        )

    def test_owner_can_edit_review(self):
        """Review owner can edit their review."""
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse(
                "edit_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.pk}
            ),
            {"rating": 4, "title": "Updated", "body": "Updated body"},
        )
        self.assertEqual(response.status_code, 302)
        self.review.refresh_from_db()
        self.assertEqual(self.review.title, "Updated")

    def test_non_owner_cannot_edit_review(self):
        """Non-owners cannot edit reviews."""
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse(
                "edit_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.pk}
            ),
            {"rating": 1, "title": "Hacked", "body": "Hacked body"},
        )
        # View redirects with error message
        self.assertEqual(response.status_code, 302)
        self.review.refresh_from_db()
        self.assertEqual(self.review.title, "Original")

    def test_edit_review_get_shows_form(self):
        """GET request should show edit form."""
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse(
                "edit_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Original", response.content)


class ReviewDeleteTest(TestCase):
    """Test review deletion."""

    def setUp(self):
        """Set up test data."""
        self.owner = User.objects.create_user(
            username="deleter", email="deleter@test.com", password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="hacker", email="hacker@test.com", password="pass123"
        )
        
        # Verify emails
        EmailAddress.objects.create(
            user=self.owner, email=self.owner.email, verified=True, primary=True
        )
        EmailAddress.objects.create(
            user=self.other_user, email=self.other_user.email, verified=True, primary=True
        )
        
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        
        self.product = Product.objects.create(
            title="Delete Test",
            slug="delete-test",
            tagline="Test tagline",
            description="Test",
            content="<p>Test premium content.</p>",
            price=Decimal("9.99"),
            image_alt="Test",
            category=self.category,
        )
        self.review = Review.objects.create(
            user=self.owner,
            product=self.product,
            rating=5,
            body="Will be deleted",
        )

    def test_owner_can_delete_review(self):
        """Review owner can delete their review."""
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse(
                "delete_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.pk}
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_non_owner_cannot_delete_review(self):
        """Non-owners cannot delete reviews."""
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse(
                "delete_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.pk}
            )
        )
        # View redirects with error message
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())

    def test_delete_review_requires_post(self):
        """Delete should require POST request."""
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse(
                "delete_review",
                kwargs={"slug": self.product.slug, "review_id": self.review.pk}
            )
        )
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Review.objects.filter(pk=self.review.pk).exists())
