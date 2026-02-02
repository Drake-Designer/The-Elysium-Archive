"""Authentication backends for the accounts app."""

from typing import cast

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractUser

class CaseSensitiveAuthenticationBackend(ModelBackend):
    """Authenticate users using case sensitive matching for username and email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate a user with an exact match on username or email."""
        login = username or kwargs.get("email") or kwargs.get("login")
        if not login or not password:
            return None

        user = self._get_user_by_login(login)
        if not user:
            return None

        if not self.user_can_authenticate(user):
            return None

        if not user.check_password(password):
            return None

        return user

    def _get_user_by_login(self, login):
        """Return a user using an exact match on username or email."""
        UserModel = cast(type[AbstractUser], get_user_model())
        methods = getattr(settings, "ACCOUNT_LOGIN_METHODS", {"username"})

        lookups = []

        if "@" in login and "email" in methods:
            lookups.append(("email", login))
            if "username" in methods:
                lookups.append((UserModel.USERNAME_FIELD, login))
        else:
            if "username" in methods:
                lookups.append((UserModel.USERNAME_FIELD, login))
            if "email" in methods:
                lookups.append(("email", login))

        for field_name, value in lookups:
            try:
                user = UserModel.objects.get(**{field_name: value})
            except UserModel.DoesNotExist:
                user = None
            except UserModel.MultipleObjectsReturned:
                user = UserModel.objects.filter(**{field_name: value}).first()

            if user:
                return user

        return None
