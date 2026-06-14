"""Filter management views (operator-only) + product filter-value assignment."""

from __future__ import annotations

from typing import Any

from django.db import models, transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Category, Product

from .models import CategoryFilter, ProductFilterValue
from .serializers import (
    CategoryFilterSerializer,
    CategoryFilterWriteSerializer,
    ProductFilterValueSerializer,
    ProductFilterValueWriteSerializer,
)


class CategoryFiltersView(generics.ListCreateAPIView):
    """GET/POST /api/v1/categories/{category_id}/filters"""

    pagination_class = None  # spec returns plain array, not paginated

    def get_category(self) -> Category:
        return get_object_or_404(Category, pk=self.kwargs["category_id"])

    def get_queryset(self) -> models.QuerySet[CategoryFilter]:
        return (
            CategoryFilter.objects.filter(category=self.get_category())
            .prefetch_related("options")
            .order_by("position")
        )

    def get_serializer_class(self) -> type[CategoryFilterSerializer]:
        return CategoryFilterSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        category = self.get_category()
        write = CategoryFilterWriteSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        write.is_valid(raise_exception=True)
        instance: CategoryFilter = write.save(category=category)
        read = CategoryFilterSerializer(instance, context=self.get_serializer_context())
        return Response(read.data, status=status.HTTP_201_CREATED)


class FilterDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PUT/DELETE /api/v1/filters/{pk}"""

    queryset = CategoryFilter.objects.all().prefetch_related("options")
    http_method_names = ["put", "delete", "options", "head"]

    def get_serializer_class(self) -> type[CategoryFilterWriteSerializer]:
        return CategoryFilterWriteSerializer


class ProductFilterValuesView(APIView):
    """PUT /api/v1/products/{product_id}/filter-values

    Replaces all filter values for the product.
    Validates that filters belong to the product's category.
    """

    def put(self, request: Request, product_id: int) -> Response:
        product = get_object_or_404(
            Product.objects.select_related("category"), pk=product_id
        )

        serializer = ProductFilterValueWriteSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated: list[dict[str, Any]] = serializer.validated_data

        # Ensure every filter belongs to this product's category
        category_filter_ids = set(
            CategoryFilter.objects.filter(category=product.category).values_list("id", flat=True)
        )
        for item in validated:
            if item["filter"].pk not in category_filter_ids:
                return Response(
                    {
                        "code": "invalid_filter",
                        "message": (
                            f"Filter {item['filter'].pk} does not belong to"
                            " this product's category."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            product.filter_values.all().delete()
            new_values: list[ProductFilterValue] = []
            for item in validated:
                new_values.append(
                    ProductFilterValue(
                        product=product,
                        filter=item["filter"],
                        option=item.get("option"),
                        value_number=item.get("valueNumber"),
                        value_boolean=item.get("valueBoolean"),
                    )
                )
            ProductFilterValue.objects.bulk_create(new_values)

        saved = ProductFilterValue.objects.filter(product=product).select_related(
            "filter", "option"
        )
        return Response(ProductFilterValueSerializer(saved, many=True).data)
