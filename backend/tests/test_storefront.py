"""TASK-012: Storefront read + filtering API tests."""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from catalog.models import Category, Product
from filters.models import CategoryFilter, CategoryFilterOption, ProductFilterValue


@pytest.fixture
def store(db: None):  # type: ignore[no-untyped-def]
    """Set up a category tree with products and filters."""
    root = Category.objects.create(name="Food")
    sub = Category.objects.create(name="Sauces", parent=root)

    heat_f = CategoryFilter.objects.create(
        category=sub, name="Heat", type=CategoryFilter.FilterType.CHOICE
    )
    mild = CategoryFilterOption.objects.create(filter=heat_f, label="Mild", value="mild", position=0)
    hot = CategoryFilterOption.objects.create(filter=heat_f, label="Hot", value="hot", position=1)

    tags_f = CategoryFilter.objects.create(
        category=sub, name="Tags", type=CategoryFilter.FilterType.MULTICHOICE
    )
    vegan = CategoryFilterOption.objects.create(filter=tags_f, label="Vegan", value="vegan", position=0)
    spicy = CategoryFilterOption.objects.create(filter=tags_f, label="Spicy", value="spicy", position=1)

    weight_f = CategoryFilter.objects.create(
        category=sub, name="Weight", type=CategoryFilter.FilterType.NUMBER, unit="g"
    )
    organic_f = CategoryFilter.objects.create(
        category=sub, name="Organic", type=CategoryFilter.FilterType.BOOLEAN
    )

    p1 = Product.objects.create(category=sub, name="Mild Sauce", price=Decimal("3.00"))
    p2 = Product.objects.create(category=sub, name="Hot Sauce", price=Decimal("4.00"))
    p3 = Product.objects.create(category=sub, name="Dead Sauce", price=Decimal("9.00"), is_active=False)

    ProductFilterValue.objects.create(product=p1, filter=heat_f, option=mild)
    ProductFilterValue.objects.create(product=p1, filter=weight_f, value_number=Decimal("100"))
    ProductFilterValue.objects.create(product=p1, filter=organic_f, value_boolean=True)
    ProductFilterValue.objects.create(product=p1, filter=tags_f, option=vegan)

    ProductFilterValue.objects.create(product=p2, filter=heat_f, option=hot)
    ProductFilterValue.objects.create(product=p2, filter=weight_f, value_number=Decimal("250"))
    ProductFilterValue.objects.create(product=p2, filter=organic_f, value_boolean=False)
    ProductFilterValue.objects.create(product=p2, filter=tags_f, option=spicy)
    ProductFilterValue.objects.create(product=p2, filter=tags_f, option=vegan)

    return {
        "root": root, "sub": sub, "p1": p1, "p2": p2, "p3": p3,
        "heat_f": heat_f, "mild": mild, "hot": hot,
        "tags_f": tags_f, "vegan": vegan, "spicy": spicy,
        "weight_f": weight_f, "organic_f": organic_f,
    }


class TestStorefrontCategories:
    @pytest.mark.django_db
    def test_public_tree(self, api_client: APIClient, store: dict) -> None:
        resp = api_client.get("/api/v1/storefront/categories")
        assert resp.status_code == 200
        root_node = next(n for n in resp.data if n["slug"] == "food")  # type: ignore[union-attr]
        assert len(root_node["children"]) == 1


class TestStorefrontFilters:
    @pytest.mark.django_db
    def test_category_filters(self, api_client: APIClient, store: dict) -> None:
        sub: Category = store["sub"]
        resp = api_client.get(f"/api/v1/storefront/categories/{sub.slug}/filters")
        assert resp.status_code == 200
        slugs = {f["slug"] for f in resp.data}  # type: ignore[union-attr]
        assert "heat" in slugs

    @pytest.mark.django_db
    def test_404_unknown_category(self, api_client: APIClient) -> None:
        resp = api_client.get("/api/v1/storefront/categories/nope/filters")
        assert resp.status_code == 404


class TestStorefrontProducts:
    @pytest.mark.django_db
    def test_all_active_products(self, api_client: APIClient, store: dict) -> None:
        sub: Category = store["sub"]
        resp = api_client.get(f"/api/v1/storefront/categories/{sub.slug}/products")
        assert resp.status_code == 200
        # p3 is inactive → not returned
        assert resp.data["count"] == 2  # type: ignore[index]

    @pytest.mark.django_db
    def test_single_choice_filter(self, api_client: APIClient, store: dict) -> None:
        sub: Category = store["sub"]
        resp = api_client.get(f"/api/v1/storefront/categories/{sub.slug}/products?heat=mild")
        assert resp.status_code == 200
        assert resp.data["count"] == 1  # type: ignore[index]
        assert resp.data["results"][0]["name"] == "Mild Sauce"  # type: ignore[index]

    @pytest.mark.django_db
    def test_multichoice_or(self, api_client: APIClient, store: dict) -> None:
        sub: Category = store["sub"]
        # ?tags=vegan is on both p1 and p2
        resp = api_client.get(f"/api/v1/storefront/categories/{sub.slug}/products?tags=vegan")
        assert resp.status_code == 200
        assert resp.data["count"] == 2  # type: ignore[index]

    @pytest.mark.django_db
    def test_multi_filter_and(self, api_client: APIClient, store: dict) -> None:
        sub: Category = store["sub"]
        resp = api_client.get(
            f"/api/v1/storefront/categories/{sub.slug}/products?heat=mild&organic=true"
        )
        assert resp.status_code == 200
        assert resp.data["count"] == 1  # type: ignore[index]

    @pytest.mark.django_db
    def test_number_range_filter(self, api_client: APIClient, store: dict) -> None:
        sub: Category = store["sub"]
        resp = api_client.get(
            f"/api/v1/storefront/categories/{sub.slug}/products?weight_min=200"
        )
        assert resp.status_code == 200
        assert resp.data["count"] == 1  # type: ignore[index]
        assert resp.data["results"][0]["name"] == "Hot Sauce"  # type: ignore[index]

    @pytest.mark.django_db
    def test_clear_filter(self, api_client: APIClient, store: dict) -> None:
        sub: Category = store["sub"]
        resp = api_client.get(f"/api/v1/storefront/categories/{sub.slug}/products")
        assert resp.data["count"] == 2  # type: ignore[index]

    @pytest.mark.django_db
    def test_products_include_descendants(self, api_client: APIClient, store: dict) -> None:
        root: Category = store["root"]
        resp = api_client.get(f"/api/v1/storefront/categories/{root.slug}/products")
        assert resp.status_code == 200
        assert resp.data["count"] == 2  # type: ignore[index]  # p1 and p2 from sub


class TestStorefrontProductDetail:
    @pytest.mark.django_db
    def test_product_detail(self, api_client: APIClient, store: dict) -> None:
        p1: Product = store["p1"]
        resp = api_client.get(f"/api/v1/storefront/products/{p1.slug}")
        assert resp.status_code == 200
        assert resp.data["name"] == "Mild Sauce"  # type: ignore[index]
        assert len(resp.data["filterValues"]) >= 1  # type: ignore[arg-type]

    @pytest.mark.django_db
    def test_inactive_product_hidden(self, api_client: APIClient, store: dict) -> None:
        p3: Product = store["p3"]
        resp = api_client.get(f"/api/v1/storefront/products/{p3.slug}")
        assert resp.status_code == 404
