# Architecture Pattern

## Selected Pattern: Modular Monolith

## Rationale

Based on:
- **Deployment**: Single VPS (2 vCPU / 4 GB / 40 GB), Dockerized, behind a reverse proxy.
- **Scale**: Hundreds–low-thousands of products, ~10 concurrent shoppers. No spiky traffic.
- **Team**: Solo developer, no hard deadline.
- **Stated priority**: Manage long-term complexity over shipping at all costs.

A **modular monolith** was selected because:
- A single deployable unit keeps ops trivial for a solo dev and fits the "preinstalled,
  zero-admin" model — one container set, one `docker compose up`.
- Internal module boundaries (Django apps) keep the codebase clean and let future features
  (cart, search, shopper accounts) slot in without a rewrite — honoring the long-term
  priority — while avoiding the operational overhead of microservices the scale doesn't need.
- The backend is an API (DRF) consumed by a separate React SPA, so the "frontend vs backend"
  split is real, but the backend itself stays a cohesive monolith.

## Structure

```
                         ┌───────────────────────────┐
   Shopper (web/mobile)  │      Reverse Proxy        │
   Operator (admin SPA)  │   (Caddy: auto-HTTPS,     │
            ───────────► │    routing, static)       │
                         └─────────────┬─────────────┘
                          /api/*       │   /  (static SPA assets)
                  ┌───────────────────┐│┌────────────────────────┐
                  │  Django + DRF     │││  React SPA (built w/    │
                  │  (Gunicorn)       │◄┘│  Bun, served as static)│
                  └─────────┬─────────┘  └────────────────────────┘
                            │
        ┌───────────────────┼───────────────────────────┐
        │   Modular Monolith (Django apps / modules)     │
        │                                                │
        │  accounts/   custom email user, auth           │
        │  catalog/    Category (mptt), Product, images  │
        │  filters/    CategoryFilter, Option, PFValue   │
        │  storefront/ public read API + filtering       │
        │  api/        DRF routers, serializers, schema  │
        └───────────────────┬───────────────────────────┘
                            │
                  ┌─────────▼─────────┐   ┌──────────────────┐
                  │   PostgreSQL      │   │  Media volume    │
                  │                   │   │  (product images)│
                  └───────────────────┘   └──────────────────┘
```

## Key Decisions
- **Modules as Django apps** with explicit responsibilities; cross-module access via
  service functions / imports, not by reaching into each other's internals.
- **API-first**: backend exposes a versioned REST API (`/api/v1/...`); the React SPA is a
  pure client. This makes the storefront and admin both API consumers.
- **Public vs authenticated surfaces** are separated: `storefront` endpoints are read-only
  and anonymous; management endpoints require an authenticated operator session.
- **Single Postgres instance**; product images on a mounted media volume (no S3/SaaS).
- **Reverse proxy (Caddy)** terminates TLS and serves SPA static assets — aligns with
  zero-admin (automatic HTTPS) and the no-paid-SaaS budget.

## Future Considerations
- If a module needs independent scaling (unlikely at this scale), its clean app boundary
  makes extraction into a service feasible.
- Cart/checkout becomes a new `orders` module; shopper accounts extend `accounts`; search
  can start as Postgres full-text within the monolith before any external engine.
- Caching layer (Redis) can be added in front of storefront read endpoints if concurrency
  grows well beyond the current ~10.
