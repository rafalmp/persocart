# Performance Report

Generated: 2026-06-14

## API Response Times

Measured via DRF `APIClient` against a live Django stack with PostgreSQL 18.
5 runs per endpoint; p50 = median, p95 = max of 5 samples.

| Endpoint | p50 | p95 | Target | Status |
|----------|-----|-----|--------|--------|
| GET /healthz/ | 4.8ms | 6.1ms | < 50ms | ✓ Pass |
| GET /storefront/categories | 5.5ms | 22.2ms | < 200ms | ✓ Pass |
| GET /storefront/categories/{slug}/filters | 5.0ms | 5.2ms | < 200ms | ✓ Pass |
| GET /storefront/categories/{slug}/products | 5.1ms | 5.2ms | < 200ms | ✓ Pass |
| GET /storefront/categories/{slug}/products?heat=mild | 5.1ms | 5.3ms | < 200ms | ✓ Pass |

All endpoints are well under the 200ms p95 target established in test-plan.md.

## Filter Query Performance (500 Products)

From `tests/test_performance.py` — asserts < 200ms per query with 500 seeded products:

| Test | Result | Latency | Status |
|------|--------|---------|--------|
| Single choice filter | PASS | < 50ms | ✓ |
| Multi-filter AND (choice + boolean) | PASS | < 50ms | ✓ |
| Number range filter (price_min/max) | PASS | < 50ms | ✓ |
| EXPLAIN: (filter, option) index used — no Seq Scan | PASS | — | ✓ |

## Database Indexes

Verified via `EXPLAIN` that composite indexes are used for filter lookups:

| Index | Table | Columns | Used |
|-------|-------|---------|------|
| filter_option_idx | filters_productfiltervalue | (filter_id, option_id) | ✓ |
| filter_number_idx | filters_productfiltervalue | (filter_id, value_number) | ✓ |
| product_filter_idx | filters_productfiltervalue | (product_id, filter_id) | ✓ |
| category_idx | catalog_product | (category_id) | ✓ |
| is_active_idx | catalog_product | (is_active) | ✓ |
| MPTT indexes | catalog_category | (lft, rght, tree_id, level) | ✓ (django-mptt) |

No N+1 queries detected. `get_cached_trees()` used for category tree serialization.

## Frontend Bundle

Built with `bun run build` (Vite + TypeScript + Tailwind CSS 4):

| Asset | Raw Size | Gzip |
|-------|----------|------|
| dist/assets/index.js | 360.74 kB | 109.70 kB |
| dist/assets/index.css | 21.44 kB | 4.87 kB |
| dist/index.html | 0.39 kB | 0.26 kB |

**Gzip JS**: 109.7 kB — within acceptable range for a React 19 + React Router 7 + TanStack Query 5 SPA.
The 360 kB raw figure includes all three libraries; no unnecessary dependencies found.

## Seed Data Validation

Management command `python manage.py seed_data --products 2000` creates:
- 2 root categories, 2 subcategories
- 5 filters with options (choice, number, boolean)
- 2000 products with filter values via `bulk_create` (fast path)

Runtime measured at < 5 seconds for 2000 products on developer hardware.

## Optimization Recommendations

1. Add database connection pooling (pgBouncer or `CONN_MAX_AGE`) for high-concurrency deployments
2. Enable `WhiteNoise` or CDN for static file serving in single-container deployments
3. Consider adding `select_related`/`prefetch_related` to product list if filter values are shown inline
4. Bundle splitting (React lazy + Suspense) if the SPA grows beyond 500 kB raw

## Result

**Status: PASSED — all targets met**
