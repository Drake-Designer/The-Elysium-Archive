"""
URL configuration for the products app
"""

from django.urls import path

from .views import archive_list_view

urlpatterns = [
    path("", archive_list_view, name="archive"),
]
