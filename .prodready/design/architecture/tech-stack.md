# Tech Stack

> **Note:** This supersedes the Define-phase assumption of **Tastypie**. During Design the
> REST framework was changed to **Django REST Framework (DRF)** — see
> `adr/ADR-001-framework-selection.md`. All other Define-phase stack choices are retained.

## Core

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Language (backend) | Python 3.13 | Required; mature, batteries-included ecosystem. Bumped from 3.12 — all pinned packages officially support 3.13. |
| Framework | Django 5.2 LTS | Required; pinned to the 5.2.x LTS line (supported into 2028); admin, ORM, auth, security defaults fit zero-admin + GDPR. |
| REST API | Django REST Framework 3.17 | Replaces Tastypie: actively maintained, rich serializers, integrates with `django-filter`. Django 5.2 support landed in DRF 3.16; pinned to 3.17.x (latest). |
| Category tree | django-mptt 0.18 | Required; efficient arbitrary-depth trees (MPTT). Django 5.2 support landed in 0.17; pinned to 0.18 (latest). |
| Filtering | django-filter 25.2 | Drives per-category custom filters cleanly on top of DRF. Django 5.2 support landed in 25.1; pinned to 25.2.x (latest). |
| Database | PostgreSQL 18 | Required; relational integrity, strong indexing for EAV filter queries. Bumped 16→18 for I/O and memory-handling improvements. |
| ORM | Django ORM | Built in; migrations, query API. |
| Image handling | Pillow 12 + django-imagekit 6 | Single product image + accessible responsive thumbnails (WCAG/mobile). Pillow pinned to 12.2.0 (latest) for CVE fixes since the 10.x line; imagekit pinned to 6.x (6.0 adds Django 5.2 support). |
| Language (frontend) | TypeScript 5.x | Type safety across the SPA. |
| Frontend framework | React 19.2 | Required; responsive storefront + admin SPA. Greenfield, so adopt 19 directly — 18→19 breaking changes only affect migrations; gains improved Suspense/hydration, Actions hooks, `ref`-as-prop, and a `javascript:`-URL security hardening. |
| Build/runtime (frontend) | Bun 1.x + Vite 8 | Required (Bun); fast install/build, Vite dev server + bundling. Vite bumped 5→8 (current); pairs with `@vitejs/plugin-react` for React 19. |
| Routing/data (frontend) | React Router 7, TanStack Query 5 | SPA routing + server-state caching for API reads. React Router 7 is built to bridge React 18→19 and pairs with React 19.2. |
| Styling | Tailwind CSS 4 | Rapid responsive, accessible UI; small footprint. v4: `@tailwindcss/vite` plugin (no PostCSS/autoprefixer needed), CSS-first `@theme` config (no `tailwind.config.js`), faster engine. Note: targets modern browsers (Safari 16.4+/Chrome 111+/Firefox 128+) — acceptable for the current-browser audience. |

## Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Container | Docker + Docker Compose | Portability, "preinstalled" single-host deploy. |
| App server | Gunicorn (Django) | Production WSGI server. |
| Reverse Proxy | Caddy 2 | Automatic HTTPS (zero-admin), routing, serves SPA static assets, no paid SaaS. |
| Static/media | Local volumes + WhiteNoise (Django static) | Self-hosted, no CDN/S3. |
| CI/CD | GitHub Actions | Free, integrated. |

## Development

| Tool | Purpose |
|------|---------|
| Ruff | Python linting + formatting |
| mypy | Python static type checking |
| pytest + pytest-django | Backend unit/integration tests |
| factory_boy + Faker | Test data factories |
| Biome (or ESLint + Prettier) | Frontend lint/format |
| Vitest + React Testing Library | Frontend unit/component tests |
| Playwright | E2E tests (storefront + admin flows) |
| pre-commit | Git hooks (ruff, mypy, biome) |
| axe-core / Playwright a11y | Automated WCAG checks in E2E |

## Versions

```json
{
  "python": "3.13",
  "django": "5.2.x (LTS)",
  "djangorestframework": "3.17.x",
  "django-mptt": "0.18.x",
  "django-filter": "25.2.x",
  "psycopg": "3.x",
  "argon2-cffi": "25.1.0",
  "pillow": "12.2.0",
  "django-imagekit": "6.x",
  "gunicorn": "26.0.0",
  "bun": "1.x",
  "react": "19.2.x",
  "react-router": "7.x",
  "typescript": "5.x",
  "vite": "8.x",
  "tailwindcss": "4.x",
  "playwright": "1.x",
  "postgres": "18",
  "caddy": "2.x"
}
```

## Authentication

- **Strategy:** Session-based cookie auth (DRF `SessionAuthentication`) for operators.
  Chosen over JWT — see `adr/ADR-003-authentication-strategy.md`.
- **Storage:** Server-side Django session; `HttpOnly`, `Secure`, `SameSite=Lax` cookie.
  CSRF protection enabled for unsafe methods (first-party SPA).
- **Password hashing:** Argon2 (`argon2-cffi`), set as the first `PASSWORD_HASHERS` entry.
- **Password policy:** Django validators + custom 12–64 character length validator.
- **Shoppers:** anonymous; storefront read endpoints require no authentication.

## Monitoring (Optional, self-hosted only)

- **Logging:** Django structured logging to stdout (captured by Docker); request logging
  at the proxy.
- **Error tracking:** none in MVP (no paid SaaS); optional self-hosted GlitchTip later.
- **Analytics:** none in MVP; optional self-hosted Plausible later (success metrics can be
  derived from app data — e.g. count of operators with ≥1 filter).
