"""
Forms for accounts app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


User = get_user_model()


class RegisterForm(UserCreationForm):
    """Create a new user with username and password fields."""

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        """Add simple Bootstrap classes and placeholders to fields."""
        super().__init__(*args, **kwargs)

        # Bootstrap class to every field
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        # Placeholders and autocomplete hints
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Username", "autocomplete": "username", "autofocus": True}
        )
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Password", "autocomplete": "new-password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Confirm password", "autocomplete": "new-password"}
        )


class LoginForm(AuthenticationForm):
    """Sign in a user with username and password."""

    def __init__(self, *args, **kwargs):
        """Add simple Bootstrap classes and placeholders to fields."""
        super().__init__(*args, **kwargs)

        # Bootstrap class to every field
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        # Placeholders and autocomplete hints
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Username", "autocomplete": "username", "autofocus": True}
        )
        self.fields["password"].widget.attrs.update(
            {"placeholder": "Password", "autocomplete": "current-password"}
        )
