"""API v1 root URL configuration."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("auth/", include("accounts.urls")),
    path("", include("catalog.urls")),
    path("", include("filters.urls")),
    path("storefront/", include("storefront.urls")),
]
