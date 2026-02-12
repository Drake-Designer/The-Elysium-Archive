from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile when a user is created."""
    if sender is None:
        return

    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved."""
    if sender is None:
        return

    profile, created = UserProfile.objects.get_or_create(user=instance)
    if not created:
        profile.save()
