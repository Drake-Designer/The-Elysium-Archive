"""
URL configuration for accounts app.
"""

from django.urls import include, path

from . import views

urlpatterns = [
    # Custom accounts pages (must come BEFORE allauth include)
    path("dashboard/", views.dashboard, name="account_dashboard"),
    path("archive/", views.my_archive, name="my_archive"),
    path("profile/", views.profile, name="account_profile"),
    path("delete/", views.account_delete, name="account_delete"),
    # Delegate remaining auth URLs to allauth
    path("", include("allauth.urls")),
]
