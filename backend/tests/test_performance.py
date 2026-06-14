"""TASK-022: Storefront filter-query performance validation.

Seeds ~500 products with EAV filter values and asserts multi-filter
queries stay under the latency target from test-plan.md.
"""

from __future__ import annotations

import random
import time
from decimal import Decimal

import pytest
from django.db import connection
from django.utils.text import slugify
from rest_framework.test import APIClient

from catalog.models import Category, Product
from filters.models import CategoryFilter, CategoryFilterOption, ProductFilterValue

LATENCY_BUDGET_MS = 200


@pytest.fixture
def perf_store(db: None):  # type: ignore[no-untyped-def]
    """Create 500 products with filter values for latency assertions."""
    root = Category.objects.create(name="PerfRoot")
    cat = Category.objects.create(name="PerfCat", parent=root)

    heat_f = CategoryFilter.objects.create(
        category=cat, name="Heat", type=CategoryFilter.FilterType.CHOICE
    )
    mild_opt = CategoryFilterOption.objects.create(
        filter=heat_f, label="Mild", value="mild", position=0
    )
    hot_opt = CategoryFilterOption.objects.create(  # noqa: F841
        filter=heat_f, label="Hot", value="hot", position=1
    )

    tags_f = CategoryFilter.objects.create(  # noqa: F841
        category=cat, name="Tags", type=CategoryFilter.FilterType.MULTICHOICE
    )
    price_f = CategoryFilter.objects.create(
        category=cat, name="Price", type=CategoryFilter.FilterType.NUMBER, unit="USD"
    )
    organic_f = CategoryFilter.objects.create(
        category=cat, name="Organic", type=CategoryFilter.FilterType.BOOLEAN
    )

    rng = random.Random(42)
    products = Product.objects.bulk_create(
        [
            Product(
                category=cat,
                name=f"Perf Product {i}",
                slug=slugify(f"Perf Product {i}"),
                price=Decimal(str(round(rng.uniform(1, 100), 2))),
                is_active=True,
            )
            for i in range(500)
        ]
    )

    fvs: list[ProductFilterValue] = []
    for i, p in enumerate(products):
        heat_opt = mild_opt if i % 2 == 0 else hot_opt
        fvs.append(ProductFilterValue(product=p, filter=heat_f, option=heat_opt))
        fvs.append(ProductFilterValue(product=p, filter=price_f, value_number=p.price))
        fvs.append(ProductFilterValue(product=p, filter=organic_f, value_boolean=(i % 3 == 0)))
    ProductFilterValue.objects.bulk_create(fvs)

    return {"cat": cat, "heat_f": heat_f, "mild_opt": mild_opt}


@pytest.mark.django_db
class TestFilterQueryPerformance:
    def _get(self, url: str) -> tuple[int, float]:
        client = APIClient()
        t0 = time.perf_counter()
        resp = client.get(url)
        return resp.status_code, (time.perf_counter() - t0) * 1000

    def test_single_choice_filter_latency(self, perf_store: dict) -> None:
        slug = perf_store["cat"].slug
        status, ms = self._get(f"/api/v1/storefront/categories/{slug}/products?heat=mild")
        assert status == 200
        assert ms < LATENCY_BUDGET_MS, (
            f"Single-choice filter took {ms:.1f}ms — exceeds {LATENCY_BUDGET_MS}ms budget"
        )

    def test_multi_filter_and_latency(self, perf_store: dict) -> None:
        slug = perf_store["cat"].slug
        status, ms = self._get(
            f"/api/v1/storefront/categories/{slug}/products?heat=mild&organic=true"
        )
        assert status == 200
        assert ms < LATENCY_BUDGET_MS, (
            f"Multi-filter AND query took {ms:.1f}ms — exceeds {LATENCY_BUDGET_MS}ms budget"
        )

    def test_number_range_filter_latency(self, perf_store: dict) -> None:
        slug = perf_store["cat"].slug
        status, ms = self._get(
            f"/api/v1/storefront/categories/{slug}/products?price_min=10&price_max=50"
        )
        assert status == 200
        assert ms < LATENCY_BUDGET_MS, (
            f"Number range filter took {ms:.1f}ms — exceeds {LATENCY_BUDGET_MS}ms budget"
        )

    def test_index_used_for_filter_value_lookup(self, perf_store: dict) -> None:
        """Verify the (filter, option) composite index is used — no sequential scan."""
        heat_f = perf_store["heat_f"]
        mild_opt = perf_store["mild_opt"]
        with connection.cursor() as cur:
            cur.execute(
                "EXPLAIN SELECT * FROM filters_productfiltervalue "
                "WHERE filter_id = %s AND option_id = %s",
                [heat_f.pk, mild_opt.pk],
            )
            plan = "\n".join(row[0] for row in cur.fetchall())
        assert "Seq Scan on filters_productfiltervalue" not in plan, (
            f"Expected index scan but got sequential scan:\n{plan}"
        )
