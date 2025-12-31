"""
URL configuration for elysium_archive project
"""

from django.contrib import admin
from django.urls import include, path

# Project URL patterns
urlpatterns = [
    path("", include("home.urls")),
    path("admin/", admin.site.urls),
]
