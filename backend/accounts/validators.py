"""Password validators (constraints.md: 12–64 characters)."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class LengthRangeValidator:
    """Enforce a min/max password length."""

    def __init__(self, min_length: int = 12, max_length: int = 64) -> None:
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password: str, user: object | None = None) -> None:
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password must contain at least %(min)d characters."),
                code="password_too_short",
                params={"min": self.min_length},
            )
        if len(password) > self.max_length:
            raise ValidationError(
                _("This password must contain at most %(max)d characters."),
                code="password_too_long",
                params={"max": self.max_length},
            )

    def get_help_text(self) -> str:
        return _(
            "Your password must be between %(min)d and %(max)d characters long."
        ) % {"min": self.min_length, "max": self.max_length}
