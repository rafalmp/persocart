"""TASK-005/006/007/008: Catalog model and API tests."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from catalog.models import Category, Product

# ------------------------------------------------------------------ models


class TestCategoryModel:
    @pytest.mark.django_db
    def test_root_creation(self) -> None:
        cat = Category.objects.create(name="Electronics")
        assert cat.slug == "electronics"
        assert cat.parent is None
        assert cat.level == 0

    @pytest.mark.django_db
    def test_nesting(self) -> None:
        parent = Category.objects.create(name="Clothing")
        child = Category.objects.create(name="Shirts", parent=parent)
        assert child.parent == parent
        assert child.level == 1

    @pytest.mark.django_db
    def test_slug_uniqueness_auto(self) -> None:
        Category.objects.create(name="Tools")
        cat2 = Category.objects.create(name="Tools")
        assert cat2.slug == "tools-1"

    @pytest.mark.django_db
    def test_subtree_move_integrity(self) -> None:
        root_a = Category.objects.create(name="A")
        root_b = Category.objects.create(name="B")
        child = Category.objects.create(name="Child", parent=root_a)
        # Move child to root_b
        child.parent = root_b
        child.save()
        child.refresh_from_db()
        assert child.parent == root_b


class TestProductModel:
    @pytest.mark.django_db
    def test_slug_auto_generation(self) -> None:
        cat = Category.objects.create(name="Food")
        product = Product.objects.create(category=cat, name="Hot Sauce", price=Decimal("9.99"))
        assert product.slug == "hot-sauce"

    @pytest.mark.django_db
    def test_price_negative_raises(self) -> None:
        cat = Category.objects.create(name="Food")
        product = Product(category=cat, name="Bad Product", price=Decimal("-1.00"))
        with pytest.raises(ValidationError):
            product.full_clean()

    @pytest.mark.django_db
    def test_active_flag_default(self) -> None:
        cat = Category.objects.create(name="Food")
        product = Product.objects.create(category=cat, name="Curry", price=Decimal("5.00"))
        assert product.is_active is True


# ------------------------------------------------------------------ category API


class TestCategoryAPI:
    @pytest.mark.django_db
    def test_list_requires_auth(self, api_client: APIClient) -> None:
        resp = api_client.get("/api/v1/categories")
        assert resp.status_code == 401

    @pytest.mark.django_db
    def test_create_category(self, auth_client: APIClient) -> None:
        resp = auth_client.post("/api/v1/categories", {"name": "Spices"}, format="json")
        assert resp.status_code == 201
        assert resp.data["name"] == "Spices"
        assert resp.data["slug"] == "spices"

    @pytest.mark.django_db
    def test_create_with_parent(self, auth_client: APIClient) -> None:
        parent = Category.objects.create(name="Food")
        resp = auth_client.post(
            "/api/v1/categories", {"name": "Condiments", "parent": parent.pk}, format="json"
        )
        assert resp.status_code == 201
        assert resp.data["parent"] == parent.pk

    @pytest.mark.django_db
    def test_retrieve(self, auth_client: APIClient) -> None:
        cat = Category.objects.create(name="Herbs")
        resp = auth_client.get(f"/api/v1/categories/{cat.pk}")
        assert resp.status_code == 200
        assert resp.data["id"] == cat.pk

    @pytest.mark.django_db
    def test_update(self, auth_client: APIClient) -> None:
        cat = Category.objects.create(name="Old Name")
        resp = auth_client.put(
            f"/api/v1/categories/{cat.pk}", {"name": "New Name"}, format="json"
        )
        assert resp.status_code == 200
        cat.refresh_from_db()
        assert cat.name == "New Name"

    @pytest.mark.django_db
    def test_delete(self, auth_client: APIClient) -> None:
        cat = Category.objects.create(name="Delete Me")
        resp = auth_client.delete(f"/api/v1/categories/{cat.pk}")
        assert resp.status_code == 204
        assert not Category.objects.filter(pk=cat.pk).exists()

    @pytest.mark.django_db
    def test_tree(self, auth_client: APIClient) -> None:
        root = Category.objects.create(name="Root")
        Category.objects.create(name="Child", parent=root)
        resp = auth_client.get("/api/v1/categories/tree")
        assert resp.status_code == 200
        # Root node is present with children list
        assert len(resp.data) >= 1
        root_data = next(n for n in resp.data if n["slug"] == "root")
        assert len(root_data["children"]) == 1


# ------------------------------------------------------------------ product API


class TestProductAPI:
    @pytest.fixture
    def category(self, db: None) -> Category:
        return Category.objects.create(name="Sauces")

    @pytest.mark.django_db
    def test_create_product(self, auth_client: APIClient, category: Category) -> None:
        resp = auth_client.post(
            "/api/v1/products",
            {"category": category.pk, "name": "Tabasco", "price": "4.99"},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["name"] == "Tabasco"
        assert resp.data["slug"] == "tabasco"

    @pytest.mark.django_db
    def test_negative_price_rejected(self, auth_client: APIClient, category: Category) -> None:
        resp = auth_client.post(
            "/api/v1/products",
            {"category": category.pk, "name": "Bad", "price": "-1.00"},
            format="json",
        )
        assert resp.status_code == 400

    @pytest.mark.django_db
    def test_filter_by_category(self, auth_client: APIClient, category: Category) -> None:
        other_cat = Category.objects.create(name="Other")
        Product.objects.create(category=category, name="P1", price=Decimal("1.00"))
        Product.objects.create(category=other_cat, name="P2", price=Decimal("2.00"))
        resp = auth_client.get(f"/api/v1/products?category={category.pk}")
        assert resp.status_code == 200
        assert resp.data["count"] == 1

    @pytest.mark.django_db
    def test_requires_auth(self, api_client: APIClient) -> None:
        resp = api_client.get("/api/v1/products")
        assert resp.status_code == 401
