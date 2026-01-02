"""
URL configuration for accounts app.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("allauth.urls")),
]
