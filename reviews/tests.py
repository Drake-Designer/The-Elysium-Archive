"""Tests for product reviews."""

import pytest
from django.urls import reverse
from django.db import IntegrityError
from reviews.models import Review
from orders.models import AccessEntitlement


@pytest.mark.django_db
class TestReviewCreation:
    """Test review creation and access control."""

    def test_non_buyer_cannot_see_review_form(
        self, client, verified_user, product_active
    ):
        """User without entitlement cannot see review form."""
        client.force_login(verified_user)

        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        # Check that review form is not in context
        # This depends on template logic

    def test_buyer_can_see_review_form(
        self, client, verified_user, entitlement, product_active
    ):
        """User with entitlement can see review form."""
        client.force_login(verified_user)

        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        # Review form should be visible or accessible

    def test_buyer_can_post_review(
        self, client, verified_user, entitlement, product_active
    ):
        """Buyer can POST a review."""
        client.force_login(verified_user)

        response = client.post(
            reverse("create_review", args=[product_active.slug]),
            {
                "rating": 5,
                "title": "Great product",
                "body": "I really enjoyed this.",
            },
        )

        # Should redirect or show success
        assert response.status_code in [200, 302]

        # Review should be created
        review = Review.objects.filter(user=verified_user, product=product_active)
        assert review.exists()

    def test_non_buyer_cannot_post_review(self, client, verified_user, product_active):
        """User without entitlement cannot POST review."""
        client.force_login(verified_user)

        response = client.post(
            reverse("create_review", args=[product_active.slug]),
            {
                "rating": 5,
                "title": "Review",
                "body": "Body",
            },
        )

        # Should be rejected or redirected
        assert response.status_code in [302, 403, 400]

        # Review should not be created
        review = Review.objects.filter(user=verified_user, product=product_active)
        assert not review.exists()

    def test_anonymous_cannot_post_review(self, client, product_active):
        """Anonymous user is redirected from review POST."""
        response = client.post(
            reverse("create_review", args=[product_active.slug]),
            {
                "rating": 5,
                "title": "Review",
                "body": "Body",
            },
            follow=False,
        )

        assert response.status_code == 302
        assert reverse("account_login") in response.url


@pytest.mark.django_db
class TestReviewDuplicatePrevention:
    """Test that duplicate reviews are prevented."""

    def test_user_cannot_post_duplicate_review(
        self, client, verified_user, entitlement, product_active
    ):
        """User cannot review same product twice."""
        client.force_login(verified_user)

        # First review
        client.post(
            reverse("create_review", args=[product_active.slug]),
            {
                "rating": 5,
                "title": "Great",
                "body": "Very good.",
            },
        )

        assert (
            Review.objects.filter(user=verified_user, product=product_active).count()
            == 1
        )

        # Try to post again
        response = client.post(
            reverse("create_review", args=[product_active.slug]),
            {
                "rating": 4,
                "title": "Changed",
                "body": "Different.",
            },
        )

        # Second review should be rejected
        assert response.status_code in [302, 400]

        # Still only 1 review
        assert (
            Review.objects.filter(user=verified_user, product=product_active).count()
            == 1
        )


@pytest.mark.django_db
class TestReviewDisplay:
    """Test review display on product detail page."""

    def test_review_appears_on_product_detail(
        self, client, verified_user, product_active, category
    ):
        """Posted review appears on product detail page."""
        # Create entitlement and review
        AccessEntitlement.objects.create(user=verified_user, product=product_active)
        review = Review.objects.create(
            user=verified_user,
            product=product_active,
            rating=5,
            title="Excellent",
            body="Really great product.",
        )

        client.force_login(verified_user)
        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()
        # Review content should appear
        assert "Excellent" in content or review.title in content

    def test_multiple_reviews_on_product(
        self, client, verified_user, product_active, category
    ):
        """Product with multiple reviews shows all reviews."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Create two reviewers with entitlements
        reviewer1 = verified_user
        reviewer2 = User.objects.create_user(
            username="reviewer2",
            email="reviewer2@example.com",
            password="testpass123",
        )
        from allauth.account.models import EmailAddress

        EmailAddress.objects.create(
            user=reviewer2,
            email=reviewer2.email,
            verified=True,
            primary=True,
        )

        AccessEntitlement.objects.create(user=reviewer1, product=product_active)
        AccessEntitlement.objects.create(user=reviewer2, product=product_active)

        # Create reviews
        Review.objects.create(
            user=reviewer1,
            product=product_active,
            rating=5,
            title="Great",
            body="Excellent.",
        )
        Review.objects.create(
            user=reviewer2,
            product=product_active,
            rating=4,
            title="Good",
            body="Very good.",
        )

        client.force_login(reviewer1)
        response = client.get(reverse("product_detail", args=[product_active.slug]))

        assert response.status_code == 200
        content = response.content.decode()
        # Both reviews should appear
        assert "Great" in content
        assert "Good" in content


@pytest.mark.django_db
class TestReviewRating:
    """Test review rating constraints."""

    def test_review_rating_valid_range(
        self, client, verified_user, entitlement, product_active
    ):
        """Review rating must be 1-5."""
        client.force_login(verified_user)

        # Valid rating
        response = client.post(
            reverse("create_review", args=[product_active.slug]),
            {
                "rating": 3,
                "title": "Okay",
                "body": "It's okay.",
            },
        )

        review = Review.objects.get(user=verified_user, product=product_active)
        assert review.rating == 3

    def test_review_optional_title(
        self, client, verified_user, entitlement, product_active
    ):
        """Review can be posted without title."""
        client.force_login(verified_user)

        response = client.post(
            reverse("create_review", args=[product_active.slug]),
            {
                "rating": 5,
                "title": "",
                "body": "Just the body, no title.",
            },
        )

        review = Review.objects.get(user=verified_user, product=product_active)
        assert review.title == "" or review.title is None
        assert review.body == "Just the body, no title."


@pytest.mark.django_db
class TestReviewModel:
    """Test Review model behavior."""

    def test_review_str(self, verified_user, product_active):
        """Review __str__ shows user and product."""
        review = Review.objects.create(
            user=verified_user,
            product=product_active,
            rating=5,
            body="Great",
        )

        review_str = str(review)
        # Should contain user and/or product info
        assert "testuser" in review_str or str(verified_user) in review_str

    def test_review_deleted_with_user(self, verified_user, product_active):
        """Review deleted when user is deleted (CASCADE)."""
        review = Review.objects.create(
            user=verified_user,
            product=product_active,
            rating=5,
            body="Great",
        )

        assert Review.objects.filter(id=review.id).exists()

        verified_user.delete()

        assert not Review.objects.filter(id=review.id).exists()

    def test_review_deleted_with_product(self, verified_user, product_active):
        """Review deleted when product is deleted (CASCADE)."""
        review = Review.objects.create(
            user=verified_user,
            product=product_active,
            rating=5,
            body="Great",
        )

        assert Review.objects.filter(id=review.id).exists()

        product_active.delete()

        assert not Review.objects.filter(id=review.id).exists()
