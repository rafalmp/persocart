"""Custom DRF exception handler.

DRF returns 403 for unauthenticated requests when using SessionAuthentication
(no WWW-Authenticate header is set). This handler converts those 403s to 401
to match the OpenAPI spec.
"""

from __future__ import annotations

from typing import Any

from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)
    if response is not None and response.status_code == 403:
        request = context.get("request")
        if request is not None and not request.user.is_authenticated:
            response.status_code = 401
    return response
