"""URL configuration for elysium_archive project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("accounts/", include("accounts.urls")),  
    path("accounts/", include("allauth.urls")), 
    path("archive/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("checkout/", include("checkout.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
