"""URL configuration for the cart app."""

from django.urls import path

from .views import add_to_cart, cart_view, remove_from_cart, update_cart_quantity

urlpatterns = [
    path("", cart_view, name="cart"),
    path("add/", add_to_cart, name="add_to_cart"),
    path("remove/", remove_from_cart, name="remove_from_cart"),
    path("update/", update_cart_quantity, name="update_cart_quantity"),
]
