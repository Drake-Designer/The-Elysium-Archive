"""URL configuration for the home app."""

from django.urls import path

from .views import (
    home_view,
    lore_view,
    test_error_400,
    test_error_403,
    test_error_404,
    test_error_500,
    test_errors_dashboard,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("lore/", lore_view, name="lore"),
    # Error page testing (staff-only, safe for production)
    path("_test/errors/", test_errors_dashboard, name="test_errors_dashboard"),
    path("_test/errors/400/", test_error_400, name="test_error_400"),
    path("_test/errors/403/", test_error_403, name="test_error_403"),
    path("_test/errors/404/", test_error_404, name="test_error_404"),
    path("_test/errors/500/", test_error_500, name="test_error_500"),
]
