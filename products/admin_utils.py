"""Utilities for Django admin customization."""

from typing import Any, Callable, TypeVar

# Type for admin display functions
F = TypeVar("F", bound=Callable[..., Any])


def admin_display(short_description: str, **kwargs: Any) -> Callable[[F], F]:
    """
    Decorator for Django admin display methods.

    Sets short_description and other display attributes with proper type hints.
    Eliminates the need for type: ignore comments on admin methods.

    Args:
        short_description: The column header text for the admin list display
        **kwargs: Additional Django admin display options (e.g., boolean=True)

    Usage:
        @admin_display("Purchases")
        def entitlement_count(self, obj):
            return format_html(...)

        @admin_display("Status", boolean=True)
        def is_active_badge(self, obj):
            return obj.is_active
    """

    def decorator(func: F) -> F:
        func.short_description = short_description  # type: ignore[attr-defined]

        # Support other Django admin display options
        for key, value in kwargs.items():
            setattr(func, key, value)

        return func

    return decorator
