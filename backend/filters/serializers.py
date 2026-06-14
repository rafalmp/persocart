"""Serializers for the filters app."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from .models import CategoryFilter, CategoryFilterOption, ProductFilterValue


class CategoryFilterOptionSerializer(serializers.ModelSerializer[CategoryFilterOption]):
    class Meta:
        model = CategoryFilterOption
        fields = ["id", "label", "value", "position"]


class CategoryFilterSerializer(serializers.ModelSerializer[CategoryFilter]):
    options = CategoryFilterOptionSerializer(many=True, read_only=True)

    class Meta:
        model = CategoryFilter
        fields = ["id", "category", "name", "slug", "type", "unit", "position", "options"]
        read_only_fields = ["id", "category", "slug"]


class CategoryFilterOptionWriteSerializer(serializers.Serializer[None]):
    label = serializers.CharField(max_length=120)
    value = serializers.CharField(max_length=120)
    position = serializers.IntegerField(default=0)


class CategoryFilterWriteSerializer(serializers.ModelSerializer[CategoryFilter]):
    options = CategoryFilterOptionWriteSerializer(many=True, required=False)

    class Meta:
        model = CategoryFilter
        fields = ["name", "type", "unit", "position", "options"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        filter_type = attrs.get("type", getattr(self.instance, "type", None))
        options = attrs.get("options", [])
        if filter_type in (CategoryFilter.FilterType.CHOICE, CategoryFilter.FilterType.MULTICHOICE):
            if not options and not (
                self.instance
                and self.instance.options.exists()
                and "options" not in attrs
            ):
                raise serializers.ValidationError(
                    {"options": "Options are required for choice/multichoice filters."}
                )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> CategoryFilter:
        options_data: list[dict[str, Any]] = validated_data.pop("options", [])
        category_filter = CategoryFilter.objects.create(**validated_data)
        for opt in options_data:
            CategoryFilterOption.objects.create(filter=category_filter, **opt)
        return category_filter

    def update(self, instance: CategoryFilter, validated_data: dict[str, Any]) -> CategoryFilter:
        options_data: list[dict[str, Any]] | None = validated_data.pop("options", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if options_data is not None:
            instance.options.all().delete()
            for opt in options_data:
                CategoryFilterOption.objects.create(filter=instance, **opt)
        return instance


class ProductFilterValueSerializer(serializers.ModelSerializer[ProductFilterValue]):
    valueNumber = serializers.DecimalField(  # noqa: N815
        source="value_number", max_digits=12, decimal_places=3, allow_null=True, read_only=True
    )
    valueBoolean = serializers.BooleanField(  # noqa: N815
        source="value_boolean", allow_null=True, read_only=True
    )

    class Meta:
        model = ProductFilterValue
        fields = ["id", "filter", "option", "valueNumber", "valueBoolean"]


class ProductFilterValueWriteSerializer(serializers.Serializer[None]):
    filter = serializers.PrimaryKeyRelatedField(queryset=CategoryFilter.objects.all())  # noqa: A003
    option = serializers.PrimaryKeyRelatedField(
        queryset=CategoryFilterOption.objects.all(), allow_null=True, required=False
    )
    valueNumber = serializers.DecimalField(  # noqa: N815
        max_digits=12, decimal_places=3, allow_null=True, required=False
    )
    valueBoolean = serializers.BooleanField(allow_null=True, required=False)  # noqa: N815

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        f: CategoryFilter = attrs["filter"]
        option = attrs.get("option")
        value_number = attrs.get("valueNumber")
        value_boolean = attrs.get("valueBoolean")

        if f.type == CategoryFilter.FilterType.CHOICE:
            if option is None:
                raise serializers.ValidationError({"option": "Required for choice filter."})
            if option.filter_id != f.pk:
                raise serializers.ValidationError({"option": "Option does not belong to this filter."})

        elif f.type == CategoryFilter.FilterType.MULTICHOICE:
            if option is None:
                raise serializers.ValidationError({"option": "Required for multichoice filter."})
            if option.filter_id != f.pk:
                raise serializers.ValidationError({"option": "Option does not belong to this filter."})

        elif f.type == CategoryFilter.FilterType.NUMBER:
            if value_number is None:
                raise serializers.ValidationError({"valueNumber": "Required for number filter."})

        elif f.type == CategoryFilter.FilterType.BOOLEAN:
            if value_boolean is None:
                raise serializers.ValidationError({"valueBoolean": "Required for boolean filter."})

        return attrs
