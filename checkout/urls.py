"""URL configuration for the checkout app."""

from django.urls import path

from .views import checkout_view, checkout_success, checkout_cancel

urlpatterns = [
    path("", checkout_view, name="checkout"),
    path("success/", checkout_success, name="checkout_success"),
    path("cancel/", checkout_cancel, name="checkout_cancel"),
]
