"""
URL configuration for the home app
"""

from django.urls import path

from .views import home_view

# Home app URL patterns
urlpatterns = [
    path("", home_view, name="home"),
]
