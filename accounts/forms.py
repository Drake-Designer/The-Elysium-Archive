"""Custom forms for accounts app and django-allauth integration."""

from allauth.account.forms import LoginForm, SignupForm
from django import forms


class ElysiumSignupForm(SignupForm):
    """Custom signup form with Bootstrap styling and proper field order."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Field order: username, email, password1, password2
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Choose a username",
                "autocomplete": "username",
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "your@email.com",
                "autocomplete": "email",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Create a secure password",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Repeat your password",
                "autocomplete": "new-password",
            }
        )

        # Ensure all required
        self.fields["username"].required = True
        self.fields["email"].required = True
        self.fields["password1"].required = True
        self.fields["password2"].required = True


class ElysiumLoginForm(LoginForm):
    """Custom login form with Bootstrap styling (email-only login)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Update login field (email or username)
        self.fields["login"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Email or username",
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )

        # Ensure required
        self.fields["login"].required = True
        self.fields["password"].required = True


class ProfileForm(forms.Form):
    """Form for editing user profile display name."""

    display_name = forms.CharField(
        max_length=60,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter a display name (optional)",
            }
        ),
        help_text="Optional display name shown in your profile",
    )
