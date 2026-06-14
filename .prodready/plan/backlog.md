# Implementation Backlog

Priority: **P0** must-have MVP · **P1** should-have MVP · **P2** future.
Status values: **Ready** (can start) · **Blocked** · **In Progress** · **Done**.
Each task targets < 4h and a commit-worthy, independently testable change.

> Infrastructure (Docker, CI, Makefile) is handled by `/prodready.scaffold`, not here.

---

## Sprint 1: Foundation

### TASK-001: Backend project & settings skeleton
**Priority**: P0 | **Estimate**: 3h | **Status**: Done

**Description**:
Create the Django 5.2 project with a modular app layout and base configuration.

**Acceptance Criteria**:
- [ ] Django 5.2 project created; apps `accounts`, `catalog`, `filters`, `storefront`, `api` registered.
- [ ] Split settings (base/dev/prod); secrets via env vars (12-factor).
- [ ] `PASSWORD_HASHERS` set with Argon2 first; custom 12–64 char password validator added to `AUTH_PASSWORD_VALIDATORS`.
- [ ] DRF, django-mptt, django-filter, imagekit installed and configured.
- [ ] `pyproject.toml` with ruff + mypy configured; both run clean on the skeleton.

**Blocked by**: None
**Blocks**: TASK-002, TASK-005, TASK-009

---

### TASK-002: Custom email-based user model
**Priority**: P0 | **Estimate**: 3h | **Status**: Done

**Description**:
Implement the `Operator` custom user (email login, no username) in `accounts`.

**Acceptance Criteria**:
- [ ] `Operator(AbstractBaseUser, PermissionsMixin)` with `USERNAME_FIELD = "email"`, unique email.
- [ ] `OperatorManager.create_user/create_superuser` (uses `set_password` → Argon2).
- [ ] `AUTH_USER_MODEL` set before first migration; initial migration created.
- [ ] Registered in Django admin (email-based).
- [ ] Unit tests: user/superuser creation, email uniqueness, password is Argon2-hashed.

**Blocked by**: TASK-001
**Blocks**: TASK-003

---

### TASK-003: Session auth API (login / logout / me)
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-001, US-002

**Description**:
Operator authentication via DRF `SessionAuthentication` with CSRF.

**Acceptance Criteria**:
- [ ] `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`.
- [ ] Cookies `HttpOnly`, `Secure`, `SameSite=Lax`; CSRF enforced on unsafe methods.
- [ ] Wrong credentials → generic 401 (no field-specific leak).
- [ ] `IsAuthenticated` default permission; management endpoints protected.
- [ ] Integration tests: login success/failure, logout, unauthenticated access blocked.

**Blocked by**: TASK-002
**Blocks**: TASK-006, TASK-008, TASK-010, TASK-013

---

### TASK-004: Frontend SPA scaffold
**Priority**: P0 | **Estimate**: 3h | **Status**: Done

**Description**:
Initialize the React 19 SPA (Bun + Vite 8) with routing, data layer, and styling.

**Acceptance Criteria**:
- [ ] Bun + Vite 8 + React 19.2 + TypeScript (strict) project.
- [ ] React Router 7 routes scaffolded (admin + storefront areas); TanStack Query 5 provider.
- [ ] Tailwind 4 via `@tailwindcss/vite`; `@theme` tokens from `ui/tokens.md`.
- [ ] API client with base URL + CSRF (`X-CSRFToken`) + credentials include.
- [ ] Biome (or ESLint+Prettier) configured; Vitest + RTL smoke test passes.

**Blocked by**: None
**Blocks**: TASK-013, TASK-017

---

## Sprint 2: Core Features — Catalog & Filters

### TASK-005: Category model (MPTT)
**Priority**: P0 | **Estimate**: 2h | **Status**: Done

**Description**:
Implement the arbitrary-depth `Category` tree in `catalog`.

**Acceptance Criteria**:
- [ ] `Category(MPTTModel)` with name, unique slug (auto from name), `TreeForeignKey` parent.
- [ ] Migration applied; MPTT indexes present.
- [ ] Unit tests: nesting, root creation, slug uniqueness, subtree move integrity.

**Blocked by**: TASK-001
**Blocks**: TASK-006, TASK-007, TASK-009

---

### TASK-006: Category management API
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-003, US-004

**Description**:
DRF CRUD + nested tree endpoint for categories (operator-only).

**Acceptance Criteria**:
- [ ] `GET/POST /categories`, `GET/PUT/DELETE /categories/{id}`, `GET /categories/tree`.
- [ ] Create with optional parent; move via parent update; cascade-delete behavior defined.
- [ ] `select_related`/tree queries avoid N+1.
- [ ] Integration tests for each endpoint incl. auth required.

**Blocked by**: TASK-005, TASK-003
**Blocks**: TASK-014

---

### TASK-007: Product model + image handling
**Priority**: P0 | **Estimate**: 3h | **Status**: Done

**Description**:
Implement `Product` with a single image and generated thumbnails.

**Acceptance Criteria**:
- [ ] `Product` (category FK, name, unique slug, description, price Decimal ≥ 0, image, is_active).
- [ ] Single image upload; imagekit (or Pillow) responsive thumbnail spec; required alt text field.
- [ ] Indexes on `category`, `is_active`; migration applied.
- [ ] Unit tests: price validation (reject negative), slug, active flag.

**Blocked by**: TASK-005
**Blocks**: TASK-008

---

### TASK-008: Product management API
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-005, US-006

**Description**:
DRF CRUD for products with multipart image upload (operator-only).

**Acceptance Criteria**:
- [ ] `GET/POST /products`, `GET/PUT/DELETE /products/{id}`; `category` query filter.
- [ ] Multipart create/update; negative/non-numeric price → 400.
- [ ] Inactive products excluded from storefront (verified later in TASK-012).
- [ ] Integration tests incl. validation and auth.

**Blocked by**: TASK-007, TASK-003
**Blocks**: TASK-011, TASK-015

---

### TASK-009: Filter models (core value)
**Priority**: P0 | **Estimate**: 3h | **Status**: Done

**Description**:
Implement `CategoryFilter`, `CategoryFilterOption`, `ProductFilterValue` in `filters`.

**Acceptance Criteria**:
- [ ] Models per `data-model/models.py`; type enum choice/multichoice/number/boolean; unit; position.
- [ ] Unique `(category, slug)`; indexes `(product,filter)`, `(filter,option)`, `(filter,value_number)`.
- [ ] Migration applied.
- [ ] Unit tests: typed-value integrity, ordering, option-belongs-to-filter.

**Blocked by**: TASK-001, TASK-005
**Blocks**: TASK-010, TASK-011, TASK-012

---

### TASK-010: Filter management API
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-007, US-009

**Description**:
Manage a category's filters and options (operator-only).

**Acceptance Criteria**:
- [ ] `GET/POST /categories/{id}/filters`, `PUT/DELETE /filters/{id}` (incl. nested options).
- [ ] Choice/multichoice require options; number supports unit; ordering honored.
- [ ] Deleting a filter removes its `ProductFilterValue`s (documented cascade).
- [ ] Integration tests per filter type + auth.

**Blocked by**: TASK-009, TASK-003
**Blocks**: TASK-016

---

### TASK-011: Product filter values API
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-008

**Description**:
Set a product's values for its category's filters with per-type validation.

**Acceptance Criteria**:
- [ ] `PUT /products/{id}/filter-values` (array of typed values).
- [ ] Choice → valid option only; multichoice → multiple rows; number → numeric; boolean → bool.
- [ ] Rejects values for filters not on the product's category.
- [ ] Integration tests covering each type + invalid input.

**Blocked by**: TASK-008, TASK-009
**Blocks**: TASK-015

---

### TASK-012: Storefront read + filtering API
**Priority**: P0 | **Estimate**: 4h | **Status**: Done
**Stories**: US-010, US-011, US-012

**Description**:
Public, anonymous read API with dynamic per-category filtering (django-filter).

**Acceptance Criteria**:
- [ ] `GET /storefront/categories` (tree), `/storefront/categories/{slug}/filters`,
      `/storefront/categories/{slug}/products`, `/storefront/products/{slug}`.
- [ ] Products = active items in category + descendants; filter slugs map to ORM conditions;
      AND across filters, OR within multichoice; number min/max ranges.
- [ ] No auth required; inactive products hidden.
- [ ] Integration tests: single filter, multichoice OR, multi-filter AND, range, clear.

**Blocked by**: TASK-009, TASK-008
**Blocks**: TASK-017, TASK-018, TASK-019, TASK-022

---

### TASK-013: Admin auth UI
**Priority**: P0 | **Estimate**: 2h | **Status**: Done
**Stories**: US-001, US-002

**Acceptance Criteria**:
- [ ] Login form (email + password), logout control.
- [ ] Protected admin routes redirect unauthenticated users to login.
- [ ] Auth state via TanStack Query (`/auth/me`); generic error on bad login.
- [ ] Component tests for the login form + guard.

**Blocked by**: TASK-004, TASK-003
**Blocks**: TASK-014, TASK-015, TASK-016

---

### TASK-014: Admin category tree editor UI
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-003, US-004

**Acceptance Criteria**:
- [ ] Tree view; create/rename/move/delete; cascade-delete confirmation dialog.
- [ ] Keyboard-navigable, `aria-expanded` (a11y).
- [ ] Wired to category API via TanStack Query with optimistic refresh.
- [ ] Component tests for create + delete-confirm.

**Blocked by**: TASK-013, TASK-006
**Blocks**: None

---

### TASK-015: Admin product management UI
**Priority**: P0 | **Estimate**: 4h | **Status**: Done
**Stories**: US-005, US-006, US-008

**Acceptance Criteria**:
- [ ] Product list per category; create/edit form with single image upload + alt text.
- [ ] Per-filter value editor rendering inputs by filter type (choice/multichoice/number/boolean).
- [ ] Client validation (price ≥ 0) mirroring server; inactive toggle.
- [ ] Component tests for form submit + filter-value editor.

**Blocked by**: TASK-013, TASK-008, TASK-011
**Blocks**: None

---

### TASK-016: Admin filter editor UI
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-007, US-009

**Acceptance Criteria**:
- [ ] Define filter (name, type, unit), manage options, reorder, delete (with warning).
- [ ] Type-aware option UI (options only for choice/multichoice).
- [ ] Wired to filter API; component tests for add-filter + reorder.

**Blocked by**: TASK-013, TASK-010
**Blocks**: None

---

## Sprint 3: Storefront UI, Integration & Polish

### TASK-017: Storefront category tree + product grid
**Priority**: P0 | **Estimate**: 3h | **Status**: Done
**Stories**: US-010

**Acceptance Criteria**:
- [ ] Responsive category navigation + product grid (mobile-first, 320px → desktop).
- [ ] Empty state; loading/error states.
- [ ] Keyboard navigable; image alt text rendered.
- [ ] Component tests + responsive snapshot.

**Blocked by**: TASK-012, TASK-004
**Blocks**: TASK-018, TASK-019

---

### TASK-018: Storefront filter panel
**Priority**: P0 | **Estimate**: 4h | **Status**: Done
**Stories**: US-011

**Acceptance Criteria**:
- [ ] Renders a category's filters by type; multichoice checkboxes, number range, boolean toggle.
- [ ] Apply updates product list; multichoice OR; clear restores full list; active-filter chips.
- [ ] Collapsible drawer on mobile; fully keyboard operable.
- [ ] Component + integration tests against storefront API (mocked).

**Blocked by**: TASK-017
**Blocks**: None

---

### TASK-019: Storefront product detail
**Priority**: P0 | **Estimate**: 2h | **Status**: Done
**Stories**: US-012

**Acceptance Criteria**:
- [ ] Name, description, price, image (alt text), filter values.
- [ ] Responsive and accessible at 200% zoom / 320px.
- [ ] Component test.

**Blocked by**: TASK-017
**Blocks**: None

---

### TASK-020: Global error handling & toasts
**Priority**: P1 | **Estimate**: 2h | **Status**: Done

**Acceptance Criteria**:
- [ ] Consistent API error shape consumed by SPA; error boundary.
- [ ] Toast notifications via polite `aria-live` region.
- [ ] Form-level validation error display pattern.
- [ ] Tests for error boundary + toast.

**Blocked by**: TASK-012
**Blocks**: None

---

### TASK-021: Accessibility (WCAG) pass
**Priority**: P0 | **Estimate**: 3h | **Status**: Done

**Acceptance Criteria**:
- [ ] axe-core checks integrated into Playwright E2E for key pages (no serious/critical violations).
- [ ] Focus management, visible focus rings, color contrast, tap targets ≥ 44px verified.
- [ ] `prefers-reduced-motion` honored; skip-to-content link present.

**Blocked by**: TASK-017, TASK-018, TASK-019
**Blocks**: None

---

### TASK-022: Seed data + filter-query performance validation
**Priority**: P0 | **Estimate**: 3h | **Status**: Done

**Description**:
Validate the indexed-EAV decision (ADR-005) at the upper product range.

**Acceptance Criteria**:
- [ ] Seed command/factory generating low-thousands of products with filter values.
- [ ] Benchmark multi-filter storefront queries; assert latency target (documented in test-plan).
- [ ] `EXPLAIN`-verified index usage; findings recorded; JSONB fallback noted if needed.

**Blocked by**: TASK-012
**Blocks**: None

---

### TASK-023: GDPR cookie/consent basics
**Priority**: P1 | **Estimate**: 2h | **Status**: Done

**Acceptance Criteria**:
- [ ] Only essential cookies (session/CSRF) in MVP; no third-party trackers.
- [ ] Minimal cookie notice if any non-essential cookie is introduced; privacy note in storefront footer.
- [ ] Confirm no shopper PII collected (anonymous browsing).

**Blocked by**: TASK-017
**Blocks**: None

---

## Task Summary

| Sprint | Tasks | Total Estimate |
|--------|-------|----------------|
| Sprint 1 (Foundation) | TASK-001 → TASK-004 | 12h |
| Sprint 2 (Catalog & Filters) | TASK-005 → TASK-016 | 36h |
| Sprint 3 (Storefront & Polish) | TASK-017 → TASK-023 | 19h |
| **Total** | **23 tasks** | **67h** |
