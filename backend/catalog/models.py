"""Catalog models: Category (MPTT tree) + Product."""

from __future__ import annotations

from collections.abc import Iterable

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.base import ModelBase
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name: str = models.CharField(max_length=200)  # type: ignore[assignment]
    slug: str = models.SlugField(max_length=220, unique=True, blank=True)  # type: ignore[assignment]
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    created_at: models.DateTimeField[object, object] = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField[object, object] = models.DateTimeField(auto_now=True)

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self) -> str:
        return str(self.name)

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
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    alt_text = models.CharField(max_length=300, blank=True)
    # Responsive thumbnail generated on demand by imagekit (virtual field, no DB column).
    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFit(800, 600)],
        format="WEBP",
        options={"quality": 80},
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return str(self.name)

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
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )
