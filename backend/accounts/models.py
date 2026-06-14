"""Custom email-based user model (ADR-003)."""

from __future__ import annotations

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class OperatorManager(BaseUserManager["Operator"]):
    """Manager for the email-based custom user model."""

    def create_user(self, email: str, password: str | None = None, **extra: object) -> "Operator":
        if not email:
            raise ValueError("Operators must have an email address")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)  # Argon2 via PASSWORD_HASHERS
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra: object) -> "Operator":
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class Operator(AbstractBaseUser, PermissionsMixin):
    """Shop operator; authenticates with email instead of a username."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = OperatorManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    def __str__(self) -> str:
        return self.email
