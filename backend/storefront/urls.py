from __future__ import annotations

from django.urls import path

from .views import (
    StorefrontCategoryFiltersView,
    StorefrontCategoryProductsView,
    StorefrontCategoryTreeView,
    StorefrontProductDetailView,
)

urlpatterns = [
    path("categories", StorefrontCategoryTreeView.as_view(), name="storefront-categories"),
    path(
        "categories/<slug:slug>/filters",
        StorefrontCategoryFiltersView.as_view(),
        name="storefront-category-filters",
    ),
    path(
        "categories/<slug:slug>/products",
        StorefrontCategoryProductsView.as_view(),
        name="storefront-category-products",
    ),
    path(
        "products/<slug:slug>",
        StorefrontProductDetailView.as_view(),
        name="storefront-product-detail",
    ),
]
