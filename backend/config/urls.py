"""Root URL configuration (scaffold baseline)."""

from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import path


def healthz(_request: HttpRequest) -> JsonResponse:
    """Liveness probe used by Docker HEALTHCHECK and CI."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    # /api/v1/... routes are added by the `api` app during Implement.
]
