"""
URL configuration for accounts app.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
]
