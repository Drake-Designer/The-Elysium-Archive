"""Tests for user profile management: view, edit display_name, delete account."""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from accounts.models import UserProfile
from accounts.signals import create_user_profile

User = get_user_model()

@pytest.mark.django_db
class TestProfileView:
    """Test profile view (read-only display and display_name form)."""

    def test_profile_requires_login(self, client):
        """Test that profile view requires authentication."""
        response = client.get(reverse("profile")
)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_profile_get_authenticated(self, client, verified_user):
        """Test that authenticated user can view profile page."""
        client.force_login(verified_user)
        response = client.get(reverse("profile"), follow=True
)
        assert response.status_code == 200

    def test_profile_displays_username_and_email(self, client, verified_user):
        """Test that profile page shows username and email read-only."""
        client.force_login(verified_user)
        response = client.get(reverse("profile"), follow=True
)
        content = response.content.decode()
        assert verified_user.username in content
        assert verified_user.email in content

    def test_profile_edit_display_name_get(self, client, verified_user):
        """Test that profile form is displayed with empty or current display_name."""
        client.force_login(verified_user)
        response = client.get(reverse("profile"), follow=True
)
        assert "display_name" in response.content.decode()

    def test_profile_edit_display_name_post(self, client, verified_user):
        """Test that POST updates display_name and shows success message."""
        client.force_login(verified_user)
        response = client.post(
            reverse("account_dashboard"),
            {"display_name": "Lord Dracula"},
            follow=True,
        )
        assert response.status_code == 200
        profile = UserProfile.objects.get_or_create(user=verified_user)[0]
        profile.refresh_from_db()
        assert profile.display_name == "Lord Dracula"
        messages = list(response.context["messages"])
        assert any("updated" in str(m).lower() for m in messages)

    def test_profile_edit_display_name_empty(self, client, verified_user):
        """Test that display_name can be set to empty (optional field)."""
        profile = UserProfile.objects.get_or_create(user=verified_user)[0]
        profile.display_name = "Some Name"
        profile.save()
        client.force_login(verified_user)
        response = client.post(
            reverse("account_dashboard"),
            {"display_name": ""},
            follow=True,
        )
        assert response.status_code == 200
        profile.refresh_from_db()
        assert profile.display_name == ""

    def test_profile_edit_display_name_max_length(self, client, verified_user):
        """Test that display_name respects max_length validation."""
        client.force_login(verified_user)
        long_name = "A" * 100
        response = client.post(
            reverse("account_dashboard"),
            {"display_name": long_name},
            follow=True,
        )
        assert response.status_code == 200
        profile = UserProfile.objects.get_or_create(user=verified_user)[0]
        profile.refresh_from_db()
        assert profile.display_name != long_name

    def test_profile_creation_signal_is_idempotent(self, db):
        """Ensure duplicate profile creation attempts do not error."""
        user = User.objects.create_user(
            username="signal_user",
            email="signal_user@example.com",
            password="testpass123",
        )

        create_user_profile(sender=User, instance=user, created=True)
        create_user_profile(sender=User, instance=user, created=True)

        assert UserProfile.objects.filter(user=user).count() == 1

@pytest.mark.django_db
class TestAccountDelete:
    """Test account deletion flow."""

    def test_delete_account_requires_login(self, client):
        """Test that delete account view requires authentication."""
        response = client.get(reverse("account_delete"))
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_delete_account_get_shows_confirmation(self, client, verified_user):
        """Test that GET shows confirmation page."""
        client.force_login(verified_user)
        response = client.get(reverse("account_delete"))
        assert response.status_code == 200
        assert "accounts/delete_account.html" in [
            t.name for t in response.templates
        ]
        content = response.content.decode()
        assert "Delete My Account" in content
        assert "cannot be undone" in content.lower()

    def test_delete_account_post_deletes_user(self, client, verified_user):
        """Test that POST actually deletes the user account."""
        user_id = verified_user.id
        client.force_login(verified_user)
        response = client.post(reverse("account_delete"), follow=True)
        assert response.status_code == 200
        assert not User.objects.filter(id=user_id).exists()

    def test_delete_account_post_logs_out_user(self, client, verified_user):
        """Test that POST logs out the user."""
        client.force_login(verified_user)
        response = client.post(reverse("account_delete"), follow=True)
        assert response.wsgi_request.user.is_authenticated is False

    def test_delete_account_post_redirects_home(self, client, verified_user):
        """Test that POST redirects to home page."""
        client.force_login(verified_user)
        response = client.post(reverse("account_delete"), follow=True)
        final_url = response.request["PATH_INFO"]
        assert final_url == reverse("home")

    def test_delete_account_post_shows_message(self, client, verified_user):
        """Test that POST shows a farewell message."""
        client.force_login(verified_user)
        response = client.post(reverse("account_delete"), follow=True)
        messages = list(response.context["messages"])
        assert any("deleted" in str(m).lower() for m in messages)

    def test_delete_account_removes_profile(self, client, verified_user):
        """Test that deleting user also removes associated UserProfile."""
        profile_id = verified_user.profile.id
        client.force_login(verified_user)
        client.post(reverse("account_delete"), follow=True)
        assert not UserProfile.objects.filter(id=profile_id).exists()
