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
                    "class": "review-rating-select",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "review-form-input",
                    "placeholder": "Give your review a title (optional)",
                    "maxlength": "50",
                    "data-max-length": "50",
                    "id": "review-title-input",
                }
            ),
            "body": forms.Textarea(
                attrs={
                    "class": "review-form-textarea",
                    "rows": 6,
                    "placeholder": "Share your thoughts about this archive entry (optional)...",
                    "maxlength": "1000",
                    "data-max-length": "1000",
                    "id": "review-body-input",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required=False for optional fields
        self.fields["title"].required = False
        self.fields["body"].required = False
        # Rating is already required by default
