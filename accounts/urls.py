"""URL configuration for the accounts app."""

from django.urls import include, path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="account_dashboard"),
    path("archive/", views.my_archive, name="my_archive"),
    path("profile/", views.profile, name="account_profile"),
    path("delete/", views.account_delete, name="account_delete"),
    path("", include("allauth.urls")),
]
