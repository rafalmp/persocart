from __future__ import annotations

from django.urls import path

from .views import CategoryFiltersView, FilterDetailView, ProductFilterValuesView

urlpatterns = [
    path("categories/<int:category_id>/filters", CategoryFiltersView.as_view(), name="category-filters"),
    path("filters/<int:pk>", FilterDetailView.as_view(), name="filter-detail"),
    path("products/<int:product_id>/filter-values", ProductFilterValuesView.as_view(), name="product-filter-values"),
]
