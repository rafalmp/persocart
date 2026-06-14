"""Serializers for the catalog app."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer[Category]):
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)  # noqa: N815
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)  # noqa: N815

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "level", "createdAt", "updatedAt"]
        read_only_fields = ["id", "slug", "level", "createdAt", "updatedAt"]


class CategoryNodeSerializer(serializers.ModelSerializer[Category]):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "children"]

    def get_children(self, obj: Category) -> list[dict[str, Any]]:
        return CategoryNodeSerializer(obj.get_children(), many=True).data  # type: ignore[return-value]


class CategoryWriteSerializer(serializers.ModelSerializer[Category]):
    parent = serializers.PrimaryKeyRelatedField(  # type: ignore[assignment]
        queryset=Category.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Category
        fields = ["name", "parent"]

    def create(self, validated_data: dict[str, Any]) -> Category:
        return Category.objects.create(**validated_data)

    def update(self, instance: Category, validated_data: dict[str, Any]) -> Category:
        instance.name = validated_data.get("name", instance.name)
        if "parent" in validated_data:
            instance.parent = validated_data["parent"]
        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer[Product]):
    imageUrl = serializers.SerializerMethodField()  # noqa: N815
    isActive = serializers.BooleanField(source="is_active")  # noqa: N815
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)  # noqa: N815
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)  # noqa: N815
    filterValues = serializers.SerializerMethodField()  # noqa: N815

    class Meta:
        model = Product
        fields = [
            "id", "category", "name", "slug", "description", "price",
            "imageUrl", "alt_text", "isActive", "filterValues", "createdAt", "updatedAt",
        ]
        read_only_fields = ["id", "slug", "imageUrl", "filterValues", "createdAt", "updatedAt"]

    def get_imageUrl(self, obj: Product) -> str | None:  # noqa: N802
        if not obj.image:
            return None
        request = self.context.get("request")
        url: str = obj.image.url
        return request.build_absolute_uri(url) if request else url

    def get_filterValues(self, obj: Product) -> list[dict[str, Any]]:  # noqa: N802
        from filters.serializers import ProductFilterValueSerializer
        return ProductFilterValueSerializer(  # type: ignore[return-value]
            obj.filter_values.all().select_related("filter", "option"), many=True
        ).data


class ProductWriteSerializer(serializers.ModelSerializer[Product]):
    isActive = serializers.BooleanField(source="is_active", default=True)  # noqa: N815

    class Meta:
        model = Product
        fields = ["category", "name", "description", "price", "image", "alt_text", "isActive"]

    def create(self, validated_data: dict[str, Any]) -> Product:
        validated_data["is_active"] = validated_data.pop("is_active", True)
        return Product.objects.create(**validated_data)

    def update(self, instance: Product, validated_data: dict[str, Any]) -> Product:
        if "is_active" in validated_data:
            instance.is_active = validated_data.pop("is_active")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
