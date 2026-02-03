"""Models for the accounts app."""

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


class UserProfile(models.Model):
    """Extended user profile with additional fields."""

    user: models.OneToOneField["AbstractUser"]
    display_name: models.CharField
    profile_picture: models.ImageField
    created_at: models.DateTimeField
    updated_at: models.DateTimeField

    # Django auto-generated
    id: int

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional display name (defaults to username)",
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        help_text="Profile picture (optional)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self) -> str:
        return f"Profile: {self.user.username}"

    def get_display_name(self) -> str:
        """Return display_name if set, otherwise username."""
        return self.display_name or self.user.username
