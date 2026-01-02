from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Extended user profile with additional fields."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(
        max_length=60,
        blank=True,
        help_text="Optional display name (defaults to username)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile: {self.user.username}"

    def get_display_name(self):
        """Return display_name if set, otherwise username."""
        return self.display_name or self.user.username
