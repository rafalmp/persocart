"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient

from accounts.models import Operator


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def operator(db: None) -> Operator:
    return Operator.objects.create_user(
        email="op@example.com", password="correct-horse-battery!"
    )


@pytest.fixture
def auth_client(operator: Operator) -> APIClient:
    client = APIClient()
    client.force_login(operator)
    return client
