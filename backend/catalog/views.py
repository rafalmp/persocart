"""Catalog management views (operator-only)."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from mptt.utils import get_cached_trees
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .models import Category, Product
from .serializers import (
    CategoryNodeSerializer,
    CategorySerializer,
    CategoryWriteSerializer,
    ProductSerializer,
    ProductWriteSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().select_related("parent")

    def get_serializer_class(self) -> type[BaseSerializer[Any]]:
        if self.action in ("create", "update", "partial_update"):
            return CategoryWriteSerializer
        if self.action == "tree":
            return CategoryNodeSerializer
        return CategorySerializer

    def _read_response(self, instance: Category, http_status: int) -> Response:
        serializer = CategorySerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data, status=http_status)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        write = CategoryWriteSerializer(data=request.data, context=self.get_serializer_context())
        write.is_valid(raise_exception=True)
        instance: Category = write.save()
        return self._read_response(instance, status.HTTP_201_CREATED)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        write = CategoryWriteSerializer(
            instance, data=request.data, partial=partial,
            context=self.get_serializer_context()
        )
        write.is_valid(raise_exception=True)
        updated: Category = write.save()
        return self._read_response(updated, status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def tree(self, request: Request) -> Response:
        roots = get_cached_trees(Category.objects.all())
        return Response(CategoryNodeSerializer(roots, many=True).data)


class ProductViewSet(viewsets.ModelViewSet):
    def get_queryset(self) -> QuerySet[Product]:
        qs = Product.objects.all().select_related("category").prefetch_related(
            "filter_values", "filter_values__filter", "filter_values__option"
        )
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def get_serializer_class(self) -> type[BaseSerializer[Any]]:
        if self.action in ("create", "update", "partial_update"):
            return ProductWriteSerializer
        return ProductSerializer

    def _read_response(self, instance: Product, http_status: int) -> Response:
        serializer = ProductSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data, status=http_status)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        write = ProductWriteSerializer(data=request.data, context=self.get_serializer_context())
        write.is_valid(raise_exception=True)
        instance: Product = write.save()
        return self._read_response(instance, status.HTTP_201_CREATED)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        write = ProductWriteSerializer(
            instance, data=request.data, partial=partial,
            context=self.get_serializer_context()
        )
        write.is_valid(raise_exception=True)
        updated: Product = write.save()
        return self._read_response(updated, status.HTTP_200_OK)
