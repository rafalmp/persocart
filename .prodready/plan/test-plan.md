# Test Plan

## Testing Strategy

### Test Pyramid

```
        /\
       /  \   E2E (10%)         Playwright (+ axe-core)
      /----\
     /      \  Integration (30%) pytest-django API tests, Vitest+MSW
    /--------\
   /          \ Unit (60%)       pytest (backend), Vitest+RTL (frontend)
  /------------\
```

## Unit Tests

**Coverage target**: ≥ 80% (enforced in CI; gate IMPLEMENT requires it).

### Backend — pytest + pytest-django + factory_boy

| Module | What to test |
|--------|--------------|
| accounts | user/superuser creation, email uniqueness, Argon2 hashing, password 12–64 validator |
| catalog | Category nesting/move, slug uniqueness; Product price ≥ 0, slug, active flag |
| filters | typed-value integrity per type, option-belongs-to-filter, ordering, unique (category, slug) |
| services | storefront filtering query builder (per filter type) |

**Location**: `backend/tests/unit/`

### Frontend — Vitest + React Testing Library

| Area | What to test |
|------|--------------|
| components (primitives) | render, keyboard interaction, a11y roles/labels |
| forms | product form, filter editor, filter-value editor validation |
| guards | protected-route redirect when unauthenticated |

**Location**: `frontend/tests/unit/`

## Integration Tests

### Backend API — pytest-django (DRF `APIClient`)

```
### Auth
- [ ] POST /auth/login - success (session cookie set)
- [ ] POST /auth/login - wrong password (generic 401, no field leak)
- [ ] POST /auth/login - non-existent user (generic 401)
- [ ] POST /auth/logout - ends session
- [ ] GET  /auth/me - 401 when unauthenticated

### Categories (auth required)
- [ ] GET/POST /categories, GET/PUT/DELETE /categories/{id}
- [ ] GET /categories/tree - nested structure
- [ ] move category → subtree moves; unauthorized → 401

### Products (auth required)
- [ ] CRUD /products; create with image (multipart)
- [ ] price negative/non-numeric → 400
- [ ] filter by category query param

### Filters (auth required, core value)
- [ ] GET/POST /categories/{id}/filters; PUT/DELETE /filters/{id}
- [ ] choice/multichoice require options; number unit; ordering
- [ ] delete filter cascades ProductFilterValue
- [ ] PUT /products/{id}/filter-values per type + invalid input rejected

### Storefront (public)
- [ ] GET /storefront/categories (tree)
- [ ] GET /storefront/categories/{slug}/filters
- [ ] GET /storefront/categories/{slug}/products - single filter
- [ ] ...multichoice OR within filter
- [ ] ...multiple filters AND
- [ ] ...number range (min/max)
- [ ] ...clear filters restores full list
- [ ] inactive products hidden
```

**Location**: `backend/tests/integration/`

### Frontend integration — Vitest + MSW (mocked API)

- [ ] Filter panel apply/clear updates product grid.
- [ ] Login flow sets auth state; logout clears it.

## E2E Tests

**Framework**: Playwright (+ axe-core a11y assertions). **Location**: `frontend/tests/e2e/`.
Mapped from `.prodready/define/test-scenarios/*.feature`.

```
- [ ] Operator login → reach admin; logout protects pages          (operator-auth.feature)
- [ ] Create nested category → appears in tree                      (catalog-management.feature)
- [ ] Create product with image in a category                      (catalog-management.feature)
- [ ] Define a category filter with options                        (custom-filters.feature)
- [ ] Assign filter value to a product                             (custom-filters.feature)
- [ ] Shopper browses category → sees products                     (storefront-browsing.feature)
- [ ] Shopper applies filter → list narrows; clear restores        (storefront-browsing.feature)
- [ ] Shopper opens product detail (responsive + a11y)             (storefront-browsing.feature)
- [ ] axe-core: no serious/critical violations on key pages
```

## Performance Tests (ADR-005)

- [ ] Seed low-thousands of products with filter values (TASK-022).
- [ ] Benchmark storefront category+filter queries; **target: p95 < 300 ms** server-side at
      the upper product range with up to 4 simultaneous filters.
- [ ] `EXPLAIN (ANALYZE)` confirms index usage on `ProductFilterValue`.

## Test Data

### Fixtures / factories (factory_boy)

```python
# backend/tests/factories.py
class OperatorFactory(DjangoModelFactory): ...        # email + valid 12–64 char password
class CategoryFactory(DjangoModelFactory): ...        # supports parent for nesting
class ProductFactory(DjangoModelFactory): ...         # price ≥ 0, active
class CategoryFilterFactory(DjangoModelFactory): ...  # type-parameterized
```

### Seed data

Management command `seed_demo` builds a spice-shop demo (categories, filters, products with
values) used by E2E and the performance benchmark.

## CI Integration

On every PR (see `/prodready.scaffold` CI):
1. ruff + mypy (backend); Biome/tsc (frontend)
2. pytest unit + integration (with Postgres 18 service)
3. Vitest unit + integration
4. Playwright E2E (+ axe) against a built app
5. Coverage gate ≥ 80%

## Traceability

| User Story | Feature File | E2E Test |
|------------|--------------|----------|
| US-001/002 | operator-auth.feature | auth.spec.ts |
| US-003/004 | catalog-management.feature | categories.spec.ts |
| US-005/006 | catalog-management.feature | products.spec.ts |
| US-007/009 | custom-filters.feature | filters-admin.spec.ts |
| US-008 | custom-filters.feature | product-filter-values.spec.ts |
| US-010/011/012 | storefront-browsing.feature | storefront.spec.ts |
