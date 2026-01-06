"""Custom forms for account workflows."""

from allauth.account.forms import LoginForm, SignupForm
from django import forms

from .models import UserProfile


class ElysiumSignupForm(SignupForm):
    """Style the signup form fields."""

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


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information."""

    remove_picture = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Remove profile picture"
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


# Alias for backward compatibility if needed
ProfileForm = UserProfileForm
