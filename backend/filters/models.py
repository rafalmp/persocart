"""Per-category custom filter models (core value — see ADR-005)."""

from __future__ import annotations

from collections.abc import Iterable

from django.db import models
from django.db.models.base import ModelBase
from django.utils.text import slugify

from catalog.models import Category, Product


class CategoryFilter(models.Model):
    class FilterType(models.TextChoices):
        CHOICE = "choice", "Single choice"
        MULTICHOICE = "multichoice", "Multiple choice"
        NUMBER = "number", "Number"
        BOOLEAN = "boolean", "Boolean"

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="filters")
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    type = models.CharField(max_length=12, choices=FilterType.choices)
    unit = models.CharField(max_length=20, blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"], name="uniq_filter_slug_per_category"
            )
        ]

    def __str__(self) -> str:
        return f"{self.category.name} / {self.name}"

    def save(
        self,
        *,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while (
                CategoryFilter.objects.filter(category=self.category, slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class CategoryFilterOption(models.Model):
    filter = models.ForeignKey(  # noqa: A003
        CategoryFilter, on_delete=models.CASCADE, related_name="options"
    )
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self) -> str:
        return self.label


class ProductFilterValue(models.Model):
    """One typed value per product-filter pair.

    Multichoice stores one row per selected option.
    Exactly one typed column (option, value_number, value_boolean) is set.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="filter_values")
    filter = models.ForeignKey(  # noqa: A003
        CategoryFilter, on_delete=models.CASCADE, related_name="product_values"
    )
    option = models.ForeignKey(
        CategoryFilterOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="product_values",
    )
    value_number = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["product", "filter"]),
            models.Index(fields=["filter", "option"]),
            models.Index(fields=["filter", "value_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} :: {self.filter.name}"
