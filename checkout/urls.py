"""URL configuration for checkout app."""

from django.urls import path

from .views import checkout, checkout_success, checkout_cancel
from checkout.webhooks import stripe_webhook

urlpatterns = [
    path("", checkout, name="checkout"),
    path("success/<str:order_number>/", checkout_success, name="checkout_success"),
    path("cancel/", checkout_cancel, name="checkout_cancel"),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
]
