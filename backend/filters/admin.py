from __future__ import annotations

from django.contrib import admin

from .models import CategoryFilter, CategoryFilterOption, ProductFilterValue


class CategoryFilterOptionInline(admin.TabularInline):
    model = CategoryFilterOption
    extra = 0


@admin.register(CategoryFilter)
class CategoryFilterAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "type", "position")
    list_filter = ("category", "type")
    inlines = [CategoryFilterOptionInline]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductFilterValue)
class ProductFilterValueAdmin(admin.ModelAdmin):
    list_display = ("product", "filter", "option", "value_number", "value_boolean")
    list_filter = ("filter__category",)
    raw_id_fields = ("product", "filter", "option")
