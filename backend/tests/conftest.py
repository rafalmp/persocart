"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def operator(db: None):  # type: ignore[no-untyped-def]
    return User.objects.create_user(email="op@example.com", password="correct-horse-battery!")


@pytest.fixture
def auth_client(operator: object) -> APIClient:
    client = APIClient()
    client.force_login(operator)
    return client
