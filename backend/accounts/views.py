"""Auth views: login / logout / me."""

from __future__ import annotations

from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, OperatorSerializer

_INVALID = {"code": "invalid_credentials", "message": "Invalid credentials."}


class LoginView(APIView):
    permission_classes = [AllowAny]
    # No auth class — session doesn't exist yet; CSRF not enforced on AllowAny
    authentication_classes: list[object] = []

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(_INVALID, status=status.HTTP_401_UNAUTHORIZED)
        user = authenticate(
            request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(_INVALID, status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        return Response(OperatorSerializer(user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(OperatorSerializer(request.user).data)
