# Implementation Plan

## Overview

- **Project**: persocart — a simple storefront for small specialized businesses whose core
  value is per-category custom filtering.
- **Pattern**: Modular monolith (Django apps `accounts`, `catalog`, `filters`, `storefront`,
  `api`) exposing a REST API, with a separate React SPA client.
- **Stack**: Python 3.13 · Django 5.2 LTS · DRF 3.17 · django-mptt 0.18 · django-filter
  25.2 · PostgreSQL 18 · argon2-cffi · Pillow 12 / django-imagekit 6. Frontend: React 19.2
  · React Router 7 · TanStack Query 5 · Vite 8 · Tailwind 4 · Bun.

> **Scope note:** Container, CI, and Makefile setup are produced in **`/prodready.scaffold`**
> (Phase 3.5), not here. This backlog is the *application code* work list executed in
> `/prodready.implement`. Tasks assume the scaffolded dev environment exists.

## Phases

### Phase 1: Foundation (Sprint 1)
**Goal**: Backend project skeleton, auth, and frontend shell.
- Django project + modular app skeleton + settings (Argon2, password policy 12–64).
- Custom email-based user model.
- Session-based auth API (login/logout/me) with CSRF.
- React SPA scaffold (routing, query client, Tailwind 4 tokens, CSRF-aware API client).

### Phase 2: Core Features — Catalog & Filters (Sprint 2)
**Goal**: Implement the catalog and the per-category filtering core value (API + admin UI).
- Category tree (MPTT) model + API.
- Product model (single image + thumbnails) + API.
- Filter models (CategoryFilter / Option / ProductFilterValue) + management API.
- Storefront read + dynamic per-category filtering API.
- Admin UI: auth, category tree editor, product management, filter editor.

### Phase 3: Storefront UI, Integration & Polish (Sprint 3)
**Goal**: Shopper experience, accessibility, performance validation, GDPR basics.
- Responsive storefront: category tree, product grid, filter panel, product detail.
- Global error handling, validation, toasts.
- WCAG accessibility pass (incl. automated axe checks).
- Seed data + filter-query performance validation (ADR-005).
- GDPR cookie/consent basics.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| EAV multi-filter queries slow at upper product range | High | Purpose-built indexes (ADR-005); TASK-022 seeds low-thousands products and asserts latency; JSONB escalation path documented. |
| django-imagekit 6 vs Pillow 12 compatibility | Medium | Verify at Scaffold install; fallback to direct Pillow thumbnailing or sorl-thumbnail. |
| Dynamic per-category filter → query param mapping complexity | Medium | Centralize in a storefront filtering service driven by `django-filter`; integration tests per filter type. |
| CSRF handling across SPA + session auth | Medium | Standard `csrftoken` cookie + `X-CSRFToken` header; E2E test for login + protected write. |
| WCAG regressions as UI grows | Medium | axe-core checks in Playwright E2E; per-component a11y checklist (ui/components.md). |
| Tailwind 4 modern-browser baseline | Low | Accepted for current-browser audience; documented in tech-stack.md. |

## Dependencies

External dependencies:
- [ ] None requiring paid accounts (no paid SaaS by constraint).
- [ ] PyPI + npm registry access for packages.
- [ ] Base Docker images (python:3.13-slim, postgres:18, caddy:2) — pulled in Scaffold.
