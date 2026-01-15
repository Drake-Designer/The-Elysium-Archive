"""Views for the home app."""

import logging

from allauth.account.utils import has_verified_email
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.views.generic import FormView, TemplateView

from products.models import DealBanner, Product

from .forms import ContactForm

logger = logging.getLogger(__name__)


@require_GET
def home_view(request):
    """
    Render the homepage with featured archive entries and dynamic sections.

    Displays:
    - Custom deal banners (admin-managed promotional carousel)
    - Featured archive entries (up to 6)
    - Latest archive entries (up to 3)
    """
    featured_products = (
        Product.objects.filter(is_active=True, is_featured=True)
        .select_related("category")
        .order_by("-created_at")[:6]
    )

    latest_products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-created_at")[:3]
    )

    deal_banners = (
        DealBanner.objects.filter(is_active=True)
        .select_related("product", "category")
        .order_by("order", "-created_at")[:10]
    )

    context = {
        "featured_products": featured_products,
        "latest_products": latest_products,
        "deal_banners": deal_banners,
        "user_is_verified": has_verified_email(request.user)
        if request.user.is_authenticated
        else False,
    }

    return render(request, "home/index.html", context)


@require_GET
def lore_view(request):
    """Render the lore page with world-building content."""
    return render(request, "home/lore.html")


# ==========================================
# ERROR PAGE TESTING (Staff Only)
# ==========================================


@staff_member_required
@require_GET
def test_errors_dashboard(request):
    """Render the error testing dashboard."""
    return render(request, "home/test_errors.html")


@staff_member_required
@require_GET
def test_error_400(request):
    """Render custom 400 template for local testing."""
    return render(request, "error_pages/400.html", status=400)


@staff_member_required
@require_GET
def test_error_403(request):
    """Render custom 403 template for local testing."""
    return render(request, "error_pages/403.html", status=403)


@staff_member_required
@require_GET
def test_error_404(request):
    """Render custom 404 template for local testing."""
    return render(request, "error_pages/404.html", status=404)


@staff_member_required
@require_GET
def test_error_500(request):
    """Render custom 500 template for local testing."""
    return render(request, "error_pages/500.html", status=500)


# ==========================================
# FOOTER PAGES - Covenant, Archiver, Lore
# ==========================================


class PrivacyCovenantView(TemplateView):
    """Privacy of the Covenant footer page."""
    template_name = "footer/privacy_covenant.html"
    extra_context = {"page_title": "Privacy of the Covenant"}


class TermsArchiverView(TemplateView):
    """Terms of the Archiver footer page."""
    template_name = "footer/terms_archiver.html"
    extra_context = {"page_title": "Terms of the Archiver"}


class ContactLoreView(FormView):
    """Contact the Lore footer page with contact form."""
    template_name = "footer/contact_lore.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact_lore")

    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Contact the Lore"
        return context

    def form_valid(self, form):
        """Send contact email and show a feedback message."""
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]

        full_message = (
            "New contact message from The Elysium Archive\n\n"
            f"From: {name}\n"
            f"Email: {email}\n"
            f"Subject: {subject}\n\n"
            "Message:\n"
            f"{message}\n\n"
            "---\n"
            "This message was sent through the Elysium Archive contact form.\n"
        )

        recipient = getattr(
            settings, "CONTACT_RECIPIENT_EMAIL", settings.DEFAULT_FROM_EMAIL
        )

        try:
            msg = EmailMessage(
                subject=f"[Elysium Archive Contact] {subject}",
                body=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                reply_to=[email],
            )
            msg.send(fail_silently=False)

            messages.success(
                self.request,
                "Your message has been sent to the Keeper. Expect a response within 24-48 hours.",
            )
        except Exception as exc:  # noqa: BLE001
            messages.error(
                self.request,
                "The ritual failed. Please try again or contact us directly at elysiumarchive@outlook.com",
            )
            logger.exception("Contact form email failed: %s", exc)

        return super().form_valid(form)
