"""Views for the home app."""
import logging

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from products.models import Product, DealBanner
from allauth.account.utils import has_verified_email
from .forms import ContactForm

logger = logging.getLogger(__name__)


def home_view(request):
    """
    Render the homepage with featured archive entries and dynamic sections.

    Displays:
    - Custom deal banners (admin-managed promotional carousel)
    - Featured archive entries (up to 6)
    - Latest archive entries (up to 3)
    """
    # Featured products for carousel
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category').order_by('-created_at')[:6]

    # Latest products for quick preview
    latest_products = Product.objects.filter(
        is_active=True
    ).select_related('category').order_by('-created_at')[:3]

    # Active deal banners for scrolling promotional carousel
    deal_banners = DealBanner.objects.filter(
        is_active=True
    ).select_related('product', 'category').order_by('order', '-created_at')[:10]

    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'deal_banners': deal_banners,
        'user_is_verified': has_verified_email(request.user) if request.user.is_authenticated else False,
    }

    return render(request, 'home/index.html', context)


def lore_view(request):
    """Render the lore page with world-building content."""
    return render(request, 'home/lore.html')


# ==========================================
# ERROR PAGE TESTING (Staff Only)
# ==========================================


@staff_member_required
def test_errors_dashboard(request):
    """Render the error testing dashboard. Staff only."""
    return render(request, 'home/test_errors.html')


@staff_member_required
def test_error_400(request):
    """Test 400 Bad Request page. Staff only."""
    raise SuspiciousOperation('Test 400 - Bad Request')


@staff_member_required
def test_error_403(request):
    """Test 403 Forbidden page. Staff only."""
    raise PermissionDenied('Test 403 - Forbidden')


@staff_member_required
def test_error_404(request):
    """Test 404 Not Found page. Staff only."""
    raise Http404('Test 404 - Not Found')


@staff_member_required
def test_error_500(request):
    """Test 500 Server Error page. Staff only."""
    raise Exception('Test 500 - Server Error')


# ==========================================
# FOOTER PAGES - Covenant, Archiver, Lore
# ==========================================


class PrivacyCovenantView(TemplateView):
    """Privacy of the Covenant - Footer page."""
    template_name = 'footer/privacy_covenant.html'
    extra_context = {'page_title': 'Privacy of the Covenant'}


class TermsArchiverView(TemplateView):
    """Terms of the Archiver - Footer page."""
    template_name = 'footer/terms_archiver.html'
    extra_context = {'page_title': 'Terms of the Archiver'}


class ContactLoreView(FormView):
    """Contact the Lore - Footer page with contact form."""
    template_name = 'footer/contact_lore.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact_lore')

    def get_context_data(self, **kwargs):
        """Add page title to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Contact the Lore'
        return context

    def form_valid(self, form):
        """Process valid form and send email to the Keeper."""
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']

        # Compose the email message
        full_message = f"""
New contact message from The Elysium Archive

From: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This message was sent through the Elysium Archive contact form.
        """

        recipient = getattr(settings, "CONTACT_RECIPIENT_EMAIL", settings.DEFAULT_FROM_EMAIL)

        try:
            msg = EmailMessage(
                subject=f'[Elysium Archive Contact] {subject}',
                body=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                reply_to=[email],
            )
            msg.send(fail_silently=False)

            messages.success(
                self.request,
                'Your message has been sent to the Keeper. Expect a response within 24-48 hours.'
            )
        except Exception as exc:
            messages.error(
                self.request,
                'The ritual failed. Please try again or contact us directly at elysiumarchive@outlook.com'
            )
            # Log the error in production
            if not settings.DEBUG:
                logger.error('Contact form email failed: %s', str(exc), exc_info=True)

        return super().form_valid(form)