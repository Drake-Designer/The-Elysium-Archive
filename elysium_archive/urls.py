from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from home.views import (
    PrivacyCovenantView,
    TermsArchiverView, 
    ContactLoreView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),         
    path("accounts/", include("accounts.urls")),         
    path("archive/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),  
    path("", include("home.urls")),
    path("privacy-of-the-covenant/", PrivacyCovenantView.as_view(), name='privacy_covenant'),
    path("terms-of-the-archiver/", TermsArchiverView.as_view(), name='terms_archiver'),
    path("contact-the-lore/", ContactLoreView.as_view(), name='contact_lore'),
]

# Handler per errori
handler400 = "django.views.defaults.bad_request"
handler403 = "django.views.defaults.permission_denied"
handler404 = "django.views.defaults.page_not_found"
handler500 = "django.views.defaults.server_error"

# Media files in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
