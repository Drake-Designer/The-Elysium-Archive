from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from home.views import ContactLoreView, PrivacyCovenantView, TermsArchiverView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("accounts.urls")),
    path("archive/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", include("home.urls")),
    path(
        "privacy-of-the-covenant/",
        PrivacyCovenantView.as_view(),
        name="privacy_covenant",
    ),
    path(
        "terms-of-the-archiver/",
        TermsArchiverView.as_view(),
        name="terms_archiver",
    ),
    path(
        "contact-the-lore/",
        ContactLoreView.as_view(),
        name="contact_lore",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
