"""URL configuration for checkout app."""

from django.urls import path

from .views import checkout, checkout_cancel, checkout_success, checkout_status
from .webhooks import stripe_webhook

urlpatterns = [
    path("", checkout, name="checkout"),
    path("success/<str:order_number>/", checkout_success, name="checkout_success"),
    path("status/<str:order_number>/", checkout_status, name="checkout_status"),
    path("cancel/", checkout_cancel, name="checkout_cancel"),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
    path("wh/", stripe_webhook, name="stripe_webhook_alias"),
]
