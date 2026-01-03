"""URL configuration for the home app."""

from django.urls import path

from .views import home_view, lore_view

urlpatterns = [
    path("", home_view, name="home"),
    path("lore/", lore_view, name="lore"),
]
