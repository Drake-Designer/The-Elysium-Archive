"""Forms for the reviews app."""

from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating and editing reviews."""

    class Meta:
        model = Review
        fields = ("rating", "title", "body")
        widgets = {
            "rating": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Give your review a title (optional)",
                    "maxlength": "120",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Share your thoughts about this archive entry...",
                }
            ),
        }
