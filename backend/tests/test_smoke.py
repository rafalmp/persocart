"""Scaffold smoke tests — replaced/expanded during Implement."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.test import Client


def test_healthz_ok() -> None:
    response = Client().get("/healthz/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_operator_uses_email_and_argon2() -> None:
    User = get_user_model()
    user = User.objects.create_user(email="owner@example.com", password="correct-horse-battery")
    assert user.email == "owner@example.com"
    assert user.get_username() == "owner@example.com"
    # Password is hashed with Argon2, never stored in plaintext.
    assert user.password.startswith("argon2")
    assert user.check_password("correct-horse-battery")
