"""Public storefront views — no authentication required."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from mptt.utils import get_cached_trees
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.models import Category, Product
from catalog.serializers import CategoryNodeSerializer, ProductSerializer
from filters.models import CategoryFilter
from filters.serializers import CategoryFilterSerializer


class StorefrontCategoryTreeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        roots = get_cached_trees(Category.objects.all())
        return Response(CategoryNodeSerializer(roots, many=True).data)


class StorefrontCategoryFiltersView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategoryFilterSerializer
    pagination_class = None  # spec returns plain array

    def get_queryset(self) -> QuerySet[CategoryFilter]:
        category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return (
            CategoryFilter.objects.filter(category=category)
            .prefetch_related("options")
            .order_by("position")
        )


class StorefrontCategoryProductsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self) -> QuerySet[Product]:
        slug = self.kwargs["slug"]
        category = get_object_or_404(Category, slug=slug)

        descendants = category.get_descendants(include_self=True)
        qs = (
            Product.objects.filter(category__in=descendants, is_active=True)
            .select_related("category")
            .prefetch_related("filter_values", "filter_values__filter", "filter_values__option")
        )

        qs = self._apply_filters(qs, category)
        return qs.distinct()

    def _apply_filters(self, qs: QuerySet[Product], category: Category) -> QuerySet[Product]:
        params = self.request.query_params
        category_filters = list(
            CategoryFilter.objects.filter(category=category).select_related()
        )

        for f in category_filters:
            ftype = f.type

            if ftype == CategoryFilter.FilterType.CHOICE:
                value = params.get(f.slug)
                if value:
                    qs = qs.filter(filter_values__filter=f, filter_values__option__value=value)

            elif ftype == CategoryFilter.FilterType.MULTICHOICE:
                values = params.getlist(f.slug)
                if values:
                    qs = qs.filter(
                        filter_values__filter=f, filter_values__option__value__in=values
                    )

            elif ftype == CategoryFilter.FilterType.NUMBER:
                min_val: str | None = params.get(f"{f.slug}_min")
                max_val: str | None = params.get(f"{f.slug}_max")
                if min_val is not None or max_val is not None:
                    kw: dict[str, Any] = {"filter_values__filter": f}
                    if min_val is not None:
                        kw["filter_values__value_number__gte"] = min_val
                    if max_val is not None:
                        kw["filter_values__value_number__lte"] = max_val
                    qs = qs.filter(**kw)

            elif ftype == CategoryFilter.FilterType.BOOLEAN:
                raw = params.get(f.slug)
                if raw is not None:
                    bool_val = raw.lower() in ("true", "1", "yes")
                    qs = qs.filter(filter_values__filter=f, filter_values__value_boolean=bool_val)

        return qs

    def get_serializer_context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class StorefrontProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Product]:
        return (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("filter_values", "filter_values__filter", "filter_values__option")
        )

    def get_serializer_context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
