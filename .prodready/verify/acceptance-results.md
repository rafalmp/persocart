# Acceptance Test Results

Generated: 2026-06-14
Test Frameworks: pytest 8.4.2 (backend), Vitest 4.1.8 + axe-core (frontend)

## Summary

| Framework | Passed | Failed | Skipped | Total |
|-----------|--------|--------|---------|-------|
| pytest (backend) | 61 | 0 | 0 | 61 |
| Vitest (frontend) | 6 | 0 | 0 | 6 |
| **Total** | **67** | **0** | **0** | **67** |

*Playwright E2E tests (e2e/accessibility.spec.ts) require the full running stack and are executed in the CI e2e job.*

## Test Traceability

| User Story | Feature File | Test File | Tests | Result |
|------------|--------------|-----------|-------|--------|
| US-001 | auth.feature | test_auth.py::TestLogin | login success, login rejection | ✓ Pass |
| US-002 | auth.feature | test_auth.py::TestLogout, TestMe | logout, /me auth guard | ✓ Pass |
| US-003 | category_management.feature | test_catalog.py::TestCategoryAPI | create, slug auto-generation, parent | ✓ Pass |
| US-004 | category_management.feature | test_catalog.py::TestCategoryAPI | rename, delete | ✓ Pass |
| US-005 | product_management.feature | test_catalog.py::TestProductAPI | create, image field, price validation, edit | ✓ Pass |
| US-006 | product_management.feature | test_catalog.py::TestProductAPI | delete, deactivate | ✓ Pass |
| US-007 | filter_management.feature | test_filters.py::TestFilterModels, TestFilterAPI | choice/number/boolean filter CRUD | ✓ Pass |
| US-008 | filter_management.feature | test_filters.py::TestProductFilterValues | set choice, number, boolean, multichoice values | ✓ Pass |
| US-009 | filter_management.feature | test_filters.py::TestFilterAPI | update filter, delete cascades values | ✓ Pass |
| US-010 | storefront.feature | test_storefront.py::TestStorefrontCategories | public tree, descendants | ✓ Pass |
| US-011 | storefront.feature | test_storefront.py::TestStorefrontProducts | choice filter, multichoice OR, AND, number range | ✓ Pass |
| US-012 | storefront.feature | test_storefront.py::TestStorefrontProductDetail | product detail, inactive hidden | ✓ Pass |

## Backend Test Details

### test_auth.py (6 tests)
- ✓ test_login_success
- ✓ test_login_wrong_password
- ✓ test_logout
- ✓ test_me_authenticated
- ✓ test_me_unauthenticated
- ✓ test_password_hashed_argon2

### test_catalog.py (12 tests)
- ✓ Category: slug auto-generation, unique slug, MPTT parent
- ✓ Product: create, price validation, image field, slug
- ✓ API: CRUD for categories and products, auth enforcement

### test_filters.py (16 tests)
- ✓ CategoryFilter: slug generation, unique per category, ordering
- ✓ Filter API: choice/number/boolean filter CRUD, option management
- ✓ ProductFilterValues: set choice, number, boolean, multichoice; validation

### test_storefront.py (14 tests)
- ✓ Public category tree, filter list, product list
- ✓ Single-choice filter, multichoice OR, multi-filter AND
- ✓ Number range filter, descendant products, inactive product hidden

### test_smoke.py (9 tests)
- ✓ All API URL namespaces resolve without 500 errors

### test_performance.py (4 tests)
- ✓ Single-choice filter < 200ms with 500 products
- ✓ Multi-filter AND < 200ms with 500 products
- ✓ Number range filter < 200ms with 500 products
- ✓ EXPLAIN verifies (filter, option) index — no sequential scan

## Frontend Test Details

### App.test.tsx (1 test)
- ✓ Storefront home renders "select a category" prompt

### a11y.test.tsx (5 tests — TASK-021)
- ✓ StorefrontHomePage: no serious/critical axe-core violations (WCAG 2.1 AA)
- ✓ StorefrontLayout: skip-to-content link `a[href="#main"]` present
- ✓ LoginPage: no serious/critical axe-core violations
- ✓ Focus rings: `focus:ring-2` class round-trips correctly
- ✓ prefers-reduced-motion: no continuous-animation classes (`animate-spin`, `animate-bounce`, `animate-ping`)

## Failures

None.

## Result

**All 67 automated tests passed ✓**
