"""URL configuration for the products app."""

from django.urls import path

from reviews.views import create_review, delete_review, edit_review

from .views import ArchiveReadView, ProductDetailView, ProductListView

urlpatterns = [
    path("", ProductListView.as_view(), name="archive"),
    path("<slug:slug>/review/", create_review, name="create_review"),
    path(
        "<slug:slug>/review/<int:review_id>/edit/",
        edit_review,
        name="edit_review",
    ),
    path(
        "<slug:slug>/review/<int:review_id>/delete/",
        delete_review,
        name="delete_review",
    ),
    path("<slug:slug>/read/", ArchiveReadView.as_view(), name="archive_read"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
