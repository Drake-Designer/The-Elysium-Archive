"""Type guards for Django type narrowing."""

from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser, AnonymousUser


def is_authenticated_user(
    user: "AbstractBaseUser | AnonymousUser",
) -> "TypeGuard[AbstractBaseUser]":
    """
    Type guard to narrow User | AnonymousUser to authenticated User.
    
    Note: Due to django-stubs limitations, accessing is_staff/is_superuser
    on the narrowed type still requires type: ignore comments where used.
    This guard only eliminates the union-attr errors, not attr-defined errors
    for PermissionsMixin attributes.
    
    Usage:
        if is_authenticated_user(request.user):
            # request.user is now AbstractBaseUser (not AnonymousUser)
            if request.user.is_staff:  # type: ignore[attr-defined]
                ...
    """
    return user.is_authenticated
