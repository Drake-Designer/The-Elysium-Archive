import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils.crypto import get_random_string


@pytest.mark.django_db
class TestAuthPages:
    """Test that authentication pages behave correctly for anonymous and.

    authenticated users.
    """

    def setup_method(self):
        """Set up test client."""
        self.client = Client()
        self.user_model = get_user_model()

    def _create_and_login_user(self):
        """Create and log in a standard user."""
        user = self.user_model.objects.create(
            username="testuser",
            email="test@example.com",
            is_active=True,
        )
        password = get_random_string(12)
        user.set_password(password)
        user.save(update_fields=["password"])
        logged_in = self.client.login(username="testuser", password=password)
        assert logged_in is True

    def test_login_page_get_anonymous(self):
        """Test that anonymous users can access the login page."""
        response = self.client.get(reverse("account_login"))
        assert response.status_code == 200

    def test_signup_page_get_anonymous(self):
        """Test that anonymous users can access the signup page."""
        response = self.client.get(reverse("account_signup"))
        assert response.status_code == 200

    def test_login_page_authenticated_redirects_to_home(self):
        """Test that authenticated users are redirected away from the login.

        page.
        """
        self._create_and_login_user()
        response = self.client.get(reverse("account_login"))
        assert response.status_code == 302
        assert response["Location"] == reverse("home")

    def test_signup_page_authenticated_redirects_to_home(self):
        """Test that authenticated users are redirected away from the signup.

        page.
        """
        self._create_and_login_user()
        response = self.client.get(reverse("account_signup"))
        assert response.status_code == 302
        assert response["Location"] == reverse("home")

    def test_logout_post_redirects_and_logs_out_user(self):
        """Test that POST logout redirects and ends the session."""
        self._create_and_login_user()
        response = self.client.post(reverse("account_logout"))
        assert response.status_code == 302
        self.client.get(response["Location"])
        response_after = self.client.get(reverse("home"))
        assert response_after.wsgi_request.user.is_authenticated is False
