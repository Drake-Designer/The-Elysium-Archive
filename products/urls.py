"""URL configuration for the products app."""

from django.urls import path

from reviews.views import create_review

from .views import ProductDetailView, ProductListView

urlpatterns = [
    path("", ProductListView.as_view(), name="archive"),
    path("<slug:slug>/review/", create_review, name="create_review"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
