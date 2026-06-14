# persocart

A per-category personalised shopping cart — a Django + React storefront where every product category has its own custom filter set, letting shoppers filter by the attributes that actually matter for that category (e.g. heat level for hot sauces, RAM for laptops).

## Quick Start

### Prerequisites

- Docker ≥ 25 and Docker Compose v2
- (Optional) Bun ≥ 1.x for running Playwright E2E tests locally

### Development

```bash
# Clone repository
git clone <repo-url>
cd persocart

# Copy and adjust environment
cp .env.example .env

# Start the full development stack
make dev
```

The Vite dev server with HMR is at **http://localhost:5173**.  
The Django API is at **http://localhost:8000/api/v1/**.  
Django admin is at **http://localhost:8000/admin/**.

Create a superuser to log in to the admin UI:

```bash
make superuser
```

### Running Tests

```bash
make test            # Backend (pytest) + frontend (Vitest)
make test-backend    # pytest only
make test-frontend   # Vitest only (unit + axe-core a11y)
make test-e2e        # Playwright E2E (requires full stack running)
```

### Code Quality

```bash
make lint            # ruff + mypy (backend); Biome + tsc (frontend)
make format          # ruff format + Biome format
```

### Seed Demo Data

```bash
docker compose run --rm backend python manage.py seed_data --products 2000
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes (prod) | Django secret key |
| `DJANGO_DEBUG` | No | `true` in dev, `false` in prod |
| `DJANGO_ALLOWED_HOSTS` | Yes (prod) | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Yes (prod) | Comma-separated scheme+host origins |
| `POSTGRES_DB` | Yes | Database name |
| `POSTGRES_USER` | Yes | Database user |
| `POSTGRES_PASSWORD` | Yes | Database password |
| `POSTGRES_HOST` | Yes | Database host (default: `db`) |
| `SITE_ADDRESS` | No | Caddy address (prod; default: `0.0.0.0:80`) |
| `PORT` | No | Host port to expose (prod; default: `80`) |

See `.env.example` for the full list.

## Architecture

Monorepo with two independent Docker services:

```
persocart/
├── backend/        # Django 5.2 + DRF 3.17 API
│   ├── accounts/   # Email-based operator auth (session cookies, ADR-003)
│   ├── catalog/    # Category (MPTT tree) + Product models
│   ├── filters/    # Per-category EAV filter model (core value, ADR-005)
│   └── storefront/ # Public read-only + filtering API
└── frontend/       # React 19 + React Router 7 + TanStack Query 5 SPA
    ├── pages/admin/       # Admin UI (category tree, products, filters)
    └── pages/storefront/  # Storefront (category nav, filter panel, product grid)
```

In production the **frontend** Caddy container serves the built SPA and proxies `/api/*` and `/media/*` to the **backend** gunicorn container. No separate reverse proxy needed for single-VPS deployments.

## API Documentation

Full API spec: `.prodready/design/api/openapi.yaml`

Key endpoints:

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Operator login |
| `GET` | `/api/v1/storefront/categories` | Public category tree |
| `GET` | `/api/v1/storefront/categories/{slug}/products` | Filtered product list |
| `GET` | `/api/v1/storefront/products/{slug}` | Product detail |
| `GET/POST` | `/api/v1/categories/{id}/filters` | Admin filter management |

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for the full production guide.

## License

MIT
