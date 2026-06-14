"""TASK-003: Session auth API integration tests."""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient


class TestLogin:
    @pytest.mark.django_db
    def test_login_success(self, api_client: APIClient, operator: object) -> None:
        resp = api_client.post(
            "/api/v1/auth/login",
            {"email": "op@example.com", "password": "correct-horse-battery!"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["email"] == "op@example.com"  # type: ignore[index]
        assert "isStaff" in resp.data  # type: ignore[operator]

    @pytest.mark.django_db
    def test_login_wrong_password(self, api_client: APIClient, operator: object) -> None:
        resp = api_client.post(
            "/api/v1/auth/login",
            {"email": "op@example.com", "password": "wrong-password-9999"},
            format="json",
        )
        assert resp.status_code == 401
        # Generic error — no field-specific leak
        assert "email" not in resp.data  # type: ignore[operator]
        assert "password" not in resp.data  # type: ignore[operator]
        assert resp.data["code"] == "invalid_credentials"  # type: ignore[index]

    @pytest.mark.django_db
    def test_login_wrong_email(self, api_client: APIClient, operator: object) -> None:
        resp = api_client.post(
            "/api/v1/auth/login",
            {"email": "nobody@example.com", "password": "correct-horse-battery!"},
            format="json",
        )
        assert resp.status_code == 401

    @pytest.mark.django_db
    def test_login_missing_fields(self, api_client: APIClient) -> None:
        resp = api_client.post("/api/v1/auth/login", {}, format="json")
        assert resp.status_code == 401


class TestLogout:
    @pytest.mark.django_db
    def test_logout_authenticated(self, auth_client: APIClient) -> None:
        resp = auth_client.post("/api/v1/auth/logout", format="json")
        assert resp.status_code == 204

    @pytest.mark.django_db
    def test_logout_unauthenticated(self, api_client: APIClient) -> None:
        resp = api_client.post("/api/v1/auth/logout", format="json")
        assert resp.status_code == 401


class TestMe:
    @pytest.mark.django_db
    def test_me_authenticated(self, auth_client: APIClient) -> None:
        resp = auth_client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        assert resp.data["email"] == "op@example.com"  # type: ignore[index]

    @pytest.mark.django_db
    def test_me_unauthenticated(self, api_client: APIClient) -> None:
        resp = api_client.get("/api/v1/auth/me")
        assert resp.status_code == 401
