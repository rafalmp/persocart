"""Serializers for the accounts app."""

from __future__ import annotations

from rest_framework import serializers

from .models import Operator


class OperatorSerializer(serializers.ModelSerializer[Operator]):
    isStaff = serializers.BooleanField(source="is_staff", read_only=True)
    dateJoined = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = Operator
        fields = ["id", "email", "isStaff", "dateJoined"]


class LoginSerializer(serializers.Serializer[None]):
    email = serializers.EmailField()
    password = serializers.CharField()
