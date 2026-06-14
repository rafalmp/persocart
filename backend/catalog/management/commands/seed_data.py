"""Management command to seed demo data for performance validation (TASK-022)."""

from __future__ import annotations

import random
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandParser

from catalog.models import Category, Product
from filters.models import CategoryFilter, CategoryFilterOption, ProductFilterValue


class Command(BaseCommand):
    help = "Seed categories, filters, and products for performance testing"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--products",
            type=int,
            default=2000,
            help="Number of products to create (default: 2000)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seed data before seeding",
        )

    def handle(self, *args: object, **options: object) -> None:
        n_products = int(options["products"])  # type: ignore[call-overload]
        clear = bool(options["clear"])

        if clear:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write("Cleared existing data.")

        # --- categories
        root, _ = Category.objects.get_or_create(name="Electronics")
        phones, _ = Category.objects.get_or_create(name="Phones", parent=root)
        laptops, _ = Category.objects.get_or_create(name="Laptops", parent=root)

        # --- filters on Phones
        brand_f, _ = CategoryFilter.objects.get_or_create(
            category=phones, name="Brand", defaults={"type": CategoryFilter.FilterType.CHOICE}
        )
        brands = ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi"]
        brand_opts: dict[str, CategoryFilterOption] = {}
        for i, b in enumerate(brands):
            opt, _ = CategoryFilterOption.objects.get_or_create(
                filter=brand_f, value=b.lower(), defaults={"label": b, "position": i}
            )
            brand_opts[b] = opt

        storage_f, _ = CategoryFilter.objects.get_or_create(
            category=phones, name="Storage", defaults={"type": CategoryFilter.FilterType.CHOICE}
        )
        storages = ["64GB", "128GB", "256GB", "512GB"]
        storage_opts: dict[str, CategoryFilterOption] = {}
        for i, s in enumerate(storages):
            opt, _ = CategoryFilterOption.objects.get_or_create(
                filter=storage_f, value=s.lower(), defaults={"label": s, "position": i}
            )
            storage_opts[s] = opt

        price_f, _ = CategoryFilter.objects.get_or_create(
            category=phones,
            name="Price",
            defaults={"type": CategoryFilter.FilterType.NUMBER, "unit": "USD"},
        )
        refurb_f, _ = CategoryFilter.objects.get_or_create(
            category=phones,
            name="Refurbished",
            defaults={"type": CategoryFilter.FilterType.BOOLEAN},
        )

        # --- filters on Laptops
        ram_f, _ = CategoryFilter.objects.get_or_create(
            category=laptops, name="RAM", defaults={"type": CategoryFilter.FilterType.CHOICE}
        )
        rams = ["8GB", "16GB", "32GB", "64GB"]
        ram_opts: dict[str, CategoryFilterOption] = {}
        for i, r in enumerate(rams):
            opt, _ = CategoryFilterOption.objects.get_or_create(
                filter=ram_f, value=r.lower(), defaults={"label": r, "position": i}
            )
            ram_opts[r] = opt

        # --- products
        brand_keys = list(brand_opts.keys())
        storage_keys = list(storage_opts.keys())
        ram_keys = list(ram_opts.keys())

        phone_products: list[Product] = []
        laptop_products: list[Product] = []
        phone_count = n_products * 2 // 3
        laptop_count = n_products - phone_count

        self.stdout.write(f"Creating {n_products} products...")

        # Batch-create products for speed
        phones_to_create = [
            Product(
                category=phones,
                name=f"Phone Model {i + 1}",
                price=Decimal(str(round(random.uniform(199, 1299), 2))),
                is_active=random.random() > 0.1,
            )
            for i in range(phone_count)
        ]
        created_phones = Product.objects.bulk_create(phones_to_create)
        phone_products.extend(created_phones)

        laptops_to_create = [
            Product(
                category=laptops,
                name=f"Laptop Model {i + 1}",
                price=Decimal(str(round(random.uniform(499, 2999), 2))),
                is_active=random.random() > 0.1,
            )
            for i in range(laptop_count)
        ]
        created_laptops = Product.objects.bulk_create(laptops_to_create)
        laptop_products.extend(created_laptops)

        # Assign filter values
        fv_batch: list[ProductFilterValue] = []
        for p in phone_products:
            brand = random.choice(brand_keys)
            storage = random.choice(storage_keys)
            fv_batch.append(ProductFilterValue(product=p, filter=brand_f, option=brand_opts[brand]))
            fv_batch.append(
                ProductFilterValue(product=p, filter=storage_f, option=storage_opts[storage])
            )
            fv_batch.append(
                ProductFilterValue(
                    product=p,
                    filter=price_f,
                    value_number=p.price,
                )
            )
            fv_batch.append(
                ProductFilterValue(
                    product=p,
                    filter=refurb_f,
                    value_boolean=random.random() < 0.2,
                )
            )

        for p in laptop_products:
            ram = random.choice(ram_keys)
            fv_batch.append(ProductFilterValue(product=p, filter=ram_f, option=ram_opts[ram]))

        ProductFilterValue.objects.bulk_create(fv_batch)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded: {len(phone_products)} phones + {len(laptop_products)} laptops "
                f"({len(fv_batch)} filter values)"
            )
        )
