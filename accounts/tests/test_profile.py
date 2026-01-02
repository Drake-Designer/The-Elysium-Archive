"""Tests for user profile management: view, edit display_name, delete account."""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from accounts.models import UserProfile


User = get_user_model()


@pytest.mark.django_db
class TestProfileView:
    """Test profile view (read-only display and display_name form)."""

    def setup_method(self):
        """Set up test client and test user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.profile = self.user.profile

    def test_profile_requires_login(self):
        """Test that profile view requires authentication."""
        response = self.client.get(reverse("account_profile"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_profile_get_authenticated(self):
        """Test that authenticated user can view profile page."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("account_profile"))
        assert response.status_code == 200
        assert "accounts/profile.html" in [t.name for t in response.templates]

    def test_profile_displays_username_and_email(self):
        """Test that profile page shows username and email read-only."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("account_profile"))
        content = response.content.decode()
        assert "testuser" in content
        assert "test@example.com" in content

    def test_profile_edit_display_name_get(self):
        """Test that profile form is displayed with empty or current display_name."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("account_profile"))
        assert "display_name" in response.content.decode()

    def test_profile_edit_display_name_post(self):
        """Test that POST updates display_name and shows success message."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("account_profile"),
            {"display_name": "Lord Dracula"},
            follow=True,
        )
        assert response.status_code == 200
        # Refresh from DB
        self.profile.refresh_from_db()
        assert self.profile.display_name == "Lord Dracula"
        # Check for success message
        messages = list(response.context["messages"])
        assert any("updated successfully" in str(m) for m in messages)

    def test_profile_edit_display_name_empty(self):
        """Test that display_name can be set to empty (optional field)."""
        self.profile.display_name = "Some Name"
        self.profile.save()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("account_profile"),
            {"display_name": ""},
            follow=True,
        )
        assert response.status_code == 200
        self.profile.refresh_from_db()
        assert self.profile.display_name == ""

    def test_profile_edit_display_name_max_length(self):
        """Test that display_name respects max_length validation."""
        self.client.login(username="testuser", password="testpass123")
        long_name = "A" * 100  # Exceeds max_length of 60
        response = self.client.post(
            reverse("account_profile"),
            {"display_name": long_name},
        )
        # Form should have errors
        assert response.status_code == 200
        self.profile.refresh_from_db()
        # display_name should not be updated
        assert self.profile.display_name != long_name


@pytest.mark.django_db
class TestAccountDelete:
    """Test account deletion flow."""

    def setup_method(self):
        """Set up test client and test user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_delete_account_requires_login(self):
        """Test that delete account view requires authentication."""
        response = self.client.get(reverse("account_delete"))
        # Should redirect to login
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_delete_account_get_shows_confirmation(self):
        """Test that GET shows confirmation page."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("account_delete"))
        assert response.status_code == 200
        assert "accounts/account_confirm_delete.html" in [
            t.name for t in response.templates
        ]
        content = response.content.decode()
        assert "Delete My Account" in content
        assert "cannot be undone" in content.lower()

    def test_delete_account_post_deletes_user(self):
        """Test that POST actually deletes the user account."""
        user_id = self.user.id
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("account_delete"), follow=True)
        # Should redirect to home
        assert response.status_code == 200
        # User should be deleted
        assert not User.objects.filter(id=user_id).exists()

    def test_delete_account_post_logs_out_user(self):
        """Test that POST logs out the user."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("account_delete"), follow=True)
        # After redirect, user should not be authenticated
        assert response.wsgi_request.user.is_authenticated is False

    def test_delete_account_post_redirects_home(self):
        """Test that POST redirects to home page."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("account_delete"), follow=True)
        # Should redirect to home
        final_url = response.request["PATH_INFO"]
        assert final_url == reverse("home")

    def test_delete_account_post_shows_message(self):
        """Test that POST shows a farewell message."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("account_delete"), follow=True)
        messages = list(response.context["messages"])
        assert any("deleted" in str(m).lower() for m in messages)

    def test_delete_account_removes_profile(self):
        """Test that deleting user also removes associated UserProfile."""
        profile_id = self.user.profile.id
        self.client.login(username="testuser", password="testpass123")
        self.client.post(reverse("account_delete"), follow=True)
        # Profile should be deleted (cascade delete)
        assert not UserProfile.objects.filter(id=profile_id).exists()
