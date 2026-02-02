"""App configuration for the cart app."""

from django.apps import AppConfig

class CartConfig(AppConfig):
    """Configure the cart app and load signals."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "cart"

    def ready(self) -> None:
        """Import signals when the app is ready."""
        from . import signals  # noqa: F401
