"""TASK-009/010/011: Filter models and API tests."""

from __future__ import annotations

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from catalog.models import Category, Product
from filters.models import CategoryFilter, CategoryFilterOption, ProductFilterValue


# ------------------------------------------------------------------ model tests


class TestFilterModels:
    @pytest.fixture
    def category(self, db: None) -> Category:
        return Category.objects.create(name="Peppers")

    @pytest.mark.django_db
    def test_slug_auto_generation(self, category: Category) -> None:
        f = CategoryFilter.objects.create(
            category=category, name="Heat Level", type=CategoryFilter.FilterType.CHOICE
        )
        assert f.slug == "heat-level"

    @pytest.mark.django_db
    def test_slug_unique_per_category(self, category: Category) -> None:
        CategoryFilter.objects.create(
            category=category, name="Size", type=CategoryFilter.FilterType.CHOICE
        )
        f2 = CategoryFilter.objects.create(
            category=category, name="Size", type=CategoryFilter.FilterType.NUMBER
        )
        assert f2.slug == "size-1"

    @pytest.mark.django_db
    def test_option_ordering(self, category: Category) -> None:
        f = CategoryFilter.objects.create(
            category=category, name="Color", type=CategoryFilter.FilterType.CHOICE
        )
        CategoryFilterOption.objects.create(filter=f, label="Red", value="red", position=2)
        CategoryFilterOption.objects.create(filter=f, label="Blue", value="blue", position=1)
        opts = list(f.options.all())
        assert opts[0].value == "blue"
        assert opts[1].value == "red"

    @pytest.mark.django_db
    def test_filter_ordering_by_position(self, category: Category) -> None:
        CategoryFilter.objects.create(
            category=category, name="B", type=CategoryFilter.FilterType.BOOLEAN, position=2
        )
        CategoryFilter.objects.create(
            category=category, name="A", type=CategoryFilter.FilterType.BOOLEAN, position=1
        )
        filters = list(CategoryFilter.objects.filter(category=category))
        assert filters[0].name == "A"


# ------------------------------------------------------------------ filter API


class TestFilterAPI:
    @pytest.fixture
    def category(self, db: None) -> Category:
        return Category.objects.create(name="Chiles")

    @pytest.mark.django_db
    def test_create_choice_filter(self, auth_client: APIClient, category: Category) -> None:
        resp = auth_client.post(
            f"/api/v1/categories/{category.pk}/filters",
            {
                "name": "Heat Level",
                "type": "choice",
                "options": [
                    {"label": "Mild", "value": "mild", "position": 0},
                    {"label": "Hot", "value": "hot", "position": 1},
                ],
            },
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["slug"] == "heat-level"  # type: ignore[index]
        assert len(resp.data["options"]) == 2  # type: ignore[arg-type]

    @pytest.mark.django_db
    def test_choice_filter_requires_options(self, auth_client: APIClient, category: Category) -> None:
        resp = auth_client.post(
            f"/api/v1/categories/{category.pk}/filters",
            {"name": "Color", "type": "choice", "options": []},
            format="json",
        )
        assert resp.status_code == 400

    @pytest.mark.django_db
    def test_create_number_filter(self, auth_client: APIClient, category: Category) -> None:
        resp = auth_client.post(
            f"/api/v1/categories/{category.pk}/filters",
            {"name": "Weight", "type": "number", "unit": "g"},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["unit"] == "g"  # type: ignore[index]

    @pytest.mark.django_db
    def test_update_filter(self, auth_client: APIClient, category: Category) -> None:
        f = CategoryFilter.objects.create(
            category=category, name="Old", type=CategoryFilter.FilterType.BOOLEAN
        )
        resp = auth_client.put(
            f"/api/v1/filters/{f.pk}",
            {"name": "New", "type": "boolean"},
            format="json",
        )
        assert resp.status_code == 200
        f.refresh_from_db()
        assert f.name == "New"

    @pytest.mark.django_db
    def test_delete_filter_removes_values(self, auth_client: APIClient, category: Category) -> None:
        f = CategoryFilter.objects.create(
            category=category, name="Organic", type=CategoryFilter.FilterType.BOOLEAN
        )
        product = Product.objects.create(category=category, name="P", price=Decimal("1.00"))
        ProductFilterValue.objects.create(product=product, filter=f, value_boolean=True)
        resp = auth_client.delete(f"/api/v1/filters/{f.pk}")
        assert resp.status_code == 204
        assert not ProductFilterValue.objects.filter(filter=f).exists()

    @pytest.mark.django_db
    def test_requires_auth(self, api_client: APIClient, category: Category) -> None:
        resp = api_client.get(f"/api/v1/categories/{category.pk}/filters")
        assert resp.status_code == 401


# ------------------------------------------------------------------ product filter values


class TestProductFilterValues:
    @pytest.fixture
    def setup(self, db: None):  # type: ignore[no-untyped-def]
        cat = Category.objects.create(name="Food")
        product = Product.objects.create(category=cat, name="Hot Sauce", price=Decimal("5.00"))
        choice_f = CategoryFilter.objects.create(
            category=cat, name="Heat", type=CategoryFilter.FilterType.CHOICE
        )
        opt_mild = CategoryFilterOption.objects.create(
            filter=choice_f, label="Mild", value="mild", position=0
        )
        opt_hot = CategoryFilterOption.objects.create(
            filter=choice_f, label="Hot", value="hot", position=1
        )
        num_f = CategoryFilter.objects.create(
            category=cat, name="Weight", type=CategoryFilter.FilterType.NUMBER, unit="g"
        )
        bool_f = CategoryFilter.objects.create(
            category=cat, name="Organic", type=CategoryFilter.FilterType.BOOLEAN
        )
        multi_f = CategoryFilter.objects.create(
            category=cat, name="Tags", type=CategoryFilter.FilterType.MULTICHOICE
        )
        opt_spicy = CategoryFilterOption.objects.create(
            filter=multi_f, label="Spicy", value="spicy", position=0
        )
        opt_vegan = CategoryFilterOption.objects.create(
            filter=multi_f, label="Vegan", value="vegan", position=1
        )
        return {
            "cat": cat,
            "product": product,
            "choice_f": choice_f,
            "opt_mild": opt_mild,
            "opt_hot": opt_hot,
            "num_f": num_f,
            "bool_f": bool_f,
            "multi_f": multi_f,
            "opt_spicy": opt_spicy,
            "opt_vegan": opt_vegan,
        }

    @pytest.mark.django_db
    def test_set_choice_value(self, auth_client: APIClient, setup: dict) -> None:
        p, f, opt = setup["product"], setup["choice_f"], setup["opt_mild"]
        resp = auth_client.put(
            f"/api/v1/products/{p.pk}/filter-values",
            [{"filter": f.pk, "option": opt.pk}],
            format="json",
        )
        assert resp.status_code == 200
        assert ProductFilterValue.objects.filter(product=p, filter=f, option=opt).exists()

    @pytest.mark.django_db
    def test_set_number_value(self, auth_client: APIClient, setup: dict) -> None:
        p, f = setup["product"], setup["num_f"]
        resp = auth_client.put(
            f"/api/v1/products/{p.pk}/filter-values",
            [{"filter": f.pk, "valueNumber": "150.5"}],
            format="json",
        )
        assert resp.status_code == 200

    @pytest.mark.django_db
    def test_set_boolean_value(self, auth_client: APIClient, setup: dict) -> None:
        p, f = setup["product"], setup["bool_f"]
        resp = auth_client.put(
            f"/api/v1/products/{p.pk}/filter-values",
            [{"filter": f.pk, "valueBoolean": True}],
            format="json",
        )
        assert resp.status_code == 200

    @pytest.mark.django_db
    def test_set_multichoice_values(self, auth_client: APIClient, setup: dict) -> None:
        p, f = setup["product"], setup["multi_f"]
        opt1, opt2 = setup["opt_spicy"], setup["opt_vegan"]
        resp = auth_client.put(
            f"/api/v1/products/{p.pk}/filter-values",
            [
                {"filter": f.pk, "option": opt1.pk},
                {"filter": f.pk, "option": opt2.pk},
            ],
            format="json",
        )
        assert resp.status_code == 200
        assert ProductFilterValue.objects.filter(product=p, filter=f).count() == 2

    @pytest.mark.django_db
    def test_invalid_option_for_filter(self, auth_client: APIClient, setup: dict) -> None:
        p, f = setup["product"], setup["choice_f"]
        wrong_opt = setup["opt_spicy"]  # belongs to multi_f, not choice_f
        resp = auth_client.put(
            f"/api/v1/products/{p.pk}/filter-values",
            [{"filter": f.pk, "option": wrong_opt.pk}],
            format="json",
        )
        assert resp.status_code == 400

    @pytest.mark.django_db
    def test_filter_not_on_product_category(self, auth_client: APIClient, setup: dict) -> None:
        p = setup["product"]
        other_cat = Category.objects.create(name="Other")
        other_f = CategoryFilter.objects.create(
            category=other_cat, name="Size", type=CategoryFilter.FilterType.NUMBER
        )
        resp = auth_client.put(
            f"/api/v1/products/{p.pk}/filter-values",
            [{"filter": other_f.pk, "valueNumber": "10"}],
            format="json",
        )
        assert resp.status_code == 400

    @pytest.mark.django_db
    def test_replaces_existing_values(self, auth_client: APIClient, setup: dict) -> None:
        p, f, opt = setup["product"], setup["choice_f"], setup["opt_mild"]
        ProductFilterValue.objects.create(product=p, filter=f, option=opt)
        new_opt = setup["opt_hot"]
        auth_client.put(
            f"/api/v1/products/{p.pk}/filter-values",
            [{"filter": f.pk, "option": new_opt.pk}],
            format="json",
        )
        assert ProductFilterValue.objects.filter(product=p, filter=f).count() == 1
        assert ProductFilterValue.objects.get(product=p, filter=f).option == new_opt
