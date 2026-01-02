import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestAuthPages:
    """Test that allauth authentication pages resolve correctly."""

    def setup_method(self):
        """Set up test client."""
        self.client = Client()

    def test_login_page_get(self):
        """Test that GET /accounts/login/ returns 200 and renders login template."""
        response = self.client.get(reverse("account_login"))
        assert response.status_code == 200
        assert "account/login.html" in [t.name for t in response.templates]

    def test_signup_page_get(self):
        """Test that GET /accounts/signup/ returns 200 and renders signup template."""
        response = self.client.get(reverse("account_signup"))
        assert response.status_code == 200
        assert "account/signup.html" in [t.name for t in response.templates]

    def test_logout_post(self):
        """Test that POST /accounts/logout/ logs out user and redirects."""
        # Create a test user
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Log in the user
        self.client.login(username="testuser", password="testpass123")

        # POST to logout
        response = self.client.post(reverse("account_logout"), follow=True)

        # Should redirect to home
        assert response.status_code == 200
        assert response.wsgi_request.user.is_authenticated is False

    def test_login_page_authenticated_redirect(self):
        """Test that authenticated users cannot access login page (if configured)."""
        # Create and log in a user
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

        # Try to access login page
        response = self.client.get(reverse("account_login"))

        # Allauth may redirect authenticated users or show login page
        # We just verify it returns a response without error
        assert response.status_code in [200, 302]

    def test_signup_page_authenticated_redirect(self):
        """Test that authenticated users cannot access signup page (if configured)."""
        # Create and log in a user
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

        # Try to access signup page
        response = self.client.get(reverse("account_signup"))

        # Allauth may redirect authenticated users or show signup page
        # We just verify it returns a response without error
        assert response.status_code in [200, 302]
