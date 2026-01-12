"""Forms for the home app."""
from django import forms


class ContactForm(forms.Form):
    """Contact form for sending messages to the Archive keeper."""
    
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Your Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-warning',
            'placeholder': 'Enter your name',
        })
    )
    
    email = forms.EmailField(
        required=True,
        label="Your Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-dark text-light border-warning',
            'placeholder': 'your.email@example.com',
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        required=True,
        label="Subject",
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-dark text-light border-warning',
            'placeholder': 'What brings you to the Archive?',
        })
    )
    
    message = forms.CharField(
        required=True,
        label="Message",
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-light border-warning',
            'placeholder': 'Share your thoughts with the Keeper...',
            'rows': 6,
        })
    )
