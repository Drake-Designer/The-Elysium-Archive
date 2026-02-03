"""Custom forms for account workflows."""

from typing import cast

from allauth.account.forms import LoginForm, SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import UserProfile


class ElysiumSignupForm(SignupForm):
    """Style the signup form fields and enforce unique email."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "autocomplete": "username",
                "class": "form-control",
                "placeholder": "Choose a username",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "autocomplete": "email",
                "class": "form-control",
                "placeholder": "your@email.com",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "class": "form-control",
                "placeholder": "Create a secure password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "autocomplete": "new-password",
                "class": "form-control",
                "placeholder": "Repeat your password",
            }
        )

    def clean_email(self):
        """Reject duplicate emails using a case-insensitive lookup."""
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            return email

        UserModel = get_user_model()
        if UserModel.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("An account with this email already exists."))

        return email


class ElysiumLoginForm(LoginForm):
    """Style the login form fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs.update(
            {
                "autocomplete": "username",
                "class": "form-control",
                "placeholder": "Email or username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "autocomplete": "current-password",
                "class": "form-control",
                "placeholder": "Password",
            }
        )

    def clean(self):
        """Validate login with case sensitive checks and show one warning."""
        cleaned_data = forms.Form.clean(self) or {}

        login_input = (cleaned_data.get("login") or "").strip()
        password = cleaned_data.get("password") or ""

        if not login_input or not password:
            return cleaned_data

        exact_user = self._get_user_exact(login_input)

        if exact_user:
            if not exact_user.check_password(password):
                self.add_error("password", _("Incorrect password."))
                raise ValidationError(_("Incorrect password."))

            return super().clean()

        ci_user = self._get_user_case_insensitive(login_input)

        if ci_user:
            if ci_user.check_password(password):
                self.add_error("login", _("Incorrect username or email."))
                raise ValidationError(
                    _("Incorrect username or email. Login is case sensitive.")
                )

            self.add_error("login", _("Incorrect username or email."))
            self.add_error("password", _("Incorrect password."))
            raise ValidationError(
                _(
                    "Incorrect username or email and incorrect password. Login is case sensitive."
                )
            )

        self.add_error("login", _("Incorrect username or email."))
        raise ValidationError(
            _("Incorrect username or email. Login is case sensitive.")
        )

    def _get_user_exact(self, login_input):
        """Return a user using an exact match on username or email."""
        UserModel = cast(type[AbstractUser], get_user_model())

        try:
            return UserModel.objects.get(**{UserModel.USERNAME_FIELD: login_input})
        except UserModel.DoesNotExist:
            pass
        except UserModel.MultipleObjectsReturned:
            return None

        try:
            return UserModel.objects.get(email=login_input)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            return None

    def _get_user_case_insensitive(self, login_input):
        """Return a user using a case insensitive match on username or email."""
        UserModel = cast(type[AbstractUser], get_user_model())

        username_field = UserModel.USERNAME_FIELD
        username_lookup = f"{username_field}__iexact"

        user = UserModel.objects.filter(**{username_lookup: login_input}).first()
        if user:
            return user

        return UserModel.objects.filter(email__iexact=login_input).first()


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""

    remove_picture = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Remove profile picture",
    )

    class Meta:
        model = UserProfile
        fields = ["display_name", "profile_picture"]
        widgets = {
            "display_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a display name (optional)",
                    "maxlength": "20",
                }
            ),
            "profile_picture": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
        labels = {
            "display_name": "Display Name",
            "profile_picture": "Profile Picture",
        }
        help_texts = {
            "display_name": "Max 20 characters (letters, numbers, symbols, spaces allowed)",
            "profile_picture": "Upload a profile picture (JPG, PNG, max 5MB)",
        }


ProfileForm = UserProfileForm
