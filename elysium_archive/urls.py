"""
URL configuration for elysium_archive project
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("archive/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("", include("home.urls")),
]
