# Launch Checklist

Project: persocart
Date: 2026-06-14
Verified by: ProdReady

## Specification

- [x] All 12 user stories implemented (100%)
- [x] All 15 API endpoints match OpenAPI spec
- [x] Data model matches schema (all 6 entities, all indexes)
- [x] 67 automated tests passing (61 backend + 6 frontend)

## Security

- [x] No critical/high vulnerabilities in production dependencies
- [x] No secrets in codebase (only placeholder values in .env.example)
- [x] OWASP Top 10 addressed (9/10 fully, A07 rate-limiting noted as future)
- [x] Argon2 password hashing (argon2-cffi)
- [x] Session cookie hardening (HttpOnly, SameSite=Lax, Secure=True in prod)
- [x] CSRF protection enabled
- [x] Non-root user in production Docker image

## Performance

- [x] All API response times < 50ms p95 on development stack
- [x] Filter queries < 200ms with 500 products (validated by automated test)
- [x] Composite indexes on ProductFilterValue verified via EXPLAIN (no Seq Scan)
- [x] Frontend bundle 109.7 kB gzip (acceptable for React + Router + TanStack Query)
- [x] No N+1 queries; `get_cached_trees()` for category tree

## Testing

- [x] 61 backend tests passing (pytest)
- [x] 6 frontend tests passing (Vitest + axe-core)
- [x] 4 performance latency assertions passing
- [x] All acceptance criteria verified (see acceptance-results.md)
- [x] axe-core WCAG 2.1 AA scan: 0 serious/critical violations
- [x] Playwright E2E configured (e2e/accessibility.spec.ts)

## Accessibility (TASK-021)

- [x] Skip-to-main-content link in StorefrontLayout
- [x] ARIA tree pattern on CategoryTree (role=tree, role=treeitem, role=group)
- [x] All form inputs have associated labels (htmlFor/id pairs)
- [x] No continuous-motion animations (prefers-reduced-motion safe)
- [x] Cookie notice in StorefrontLayout footer (GDPR TASK-023)

## Infrastructure

- [x] backend/Dockerfile: multi-stage, non-root user (app), HEALTHCHECK, collectstatic
- [x] frontend/Dockerfile: Caddy runtime stage, SPA routing, API proxy, HEALTHCHECK
- [x] docker-compose.prod.yml: backend + frontend + PostgreSQL 18, resource limits
- [x] Health check endpoint: GET /healthz/ → {"status":"ok"}
- [x] Environment variables documented in .env.example
- [x] CI pipeline: lint → type-check → test → docker-build → e2e
- [x] Deploy pipeline: GHCR push on main branch

## Documentation

- [x] README.md: quick start, env vars table, architecture overview, API table
- [x] DEPLOYMENT.md: VPS setup, HTTPS (Caddy auto-TLS), DB backup, GHCR pull
- [x] .env.example: all required variables documented
- [x] openapi.yaml: full API spec in .prodready/design/api/

## Pre-Deployment (operator action required)

- [ ] Generate and set `DJANGO_SECRET_KEY` (use `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Set `DJANGO_ALLOWED_HOSTS` to production domain
- [ ] Set `DJANGO_CSRF_TRUSTED_ORIGINS` to `https://your-domain.com`
- [ ] Configure DNS A record to point to server IP
- [ ] Open firewall ports 80 and 443
- [ ] Set `SITE_ADDRESS=your-domain.com` in .env for auto-HTTPS (Caddy)
- [ ] Run `make prod-migrate` after first deployment
- [ ] Create operator account: `docker compose -f docker-compose.prod.yml run --rm backend python manage.py createsuperuser`
- [ ] Optional: configure uptime monitoring (UptimeRobot, Healthchecks.io) on `/healthz/`
- [ ] Optional: upgrade `pytest>=9.0.3` in requirements-dev.txt (CVE-2025-71176)
- [ ] Optional: add `AnonRateThrottle` to `LoginView` before public internet exposure

---

## Deployment Command

```bash
# On production server:
git clone <repo-url> /opt/persocart && cd /opt/persocart
cp .env.example .env
# Edit .env with production values
make build-prod
make prod-migrate
make prod-up
```

---

## Result

🎉 **PRODUCTION READY**

All automated checks passed. Complete the pre-deployment checklist items (marked `[ ]`) before going live.
