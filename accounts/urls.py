"""URL configuration for accounts app."""

from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="account_dashboard"),
    path("my-archive/", views.my_archive, name="my_archive"),
    path("profile/", views.profile, name="profile"),
    path("delete/", views.delete_account, name="account_delete"),
]
