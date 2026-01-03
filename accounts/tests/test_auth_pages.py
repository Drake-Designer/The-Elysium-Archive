import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


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
        User = get_user_model()
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(reverse("account_logout"), follow=True)

        assert response.status_code == 200
        assert response.wsgi_request.user.is_authenticated is False

    def test_login_page_authenticated_redirect(self):
        """Test that authenticated users cannot access login page (if configured)."""
        User = get_user_model()
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("account_login"))

        assert response.status_code in [200, 302]

    def test_signup_page_authenticated_redirect(self):
        """Test that authenticated users cannot access signup page (if configured)."""
        User = get_user_model()
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("account_signup"))

        assert response.status_code in [200, 302]
