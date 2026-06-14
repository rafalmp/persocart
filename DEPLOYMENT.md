# Deployment Guide

## Overview

persocart ships as two Docker images:

- **backend** — Django/gunicorn, serves the REST API on port 8000
- **frontend** — Caddy, serves the pre-built React SPA and proxies `/api/*` + `/media/*` to the backend

`docker-compose.prod.yml` wires them together with a PostgreSQL 18 database.

---

## VPS Deployment (single-server)

### Prerequisites

- Ubuntu 22.04+ (or any Linux with Docker ≥ 25)
- Docker & Docker Compose v2 installed
- Domain name (optional, required for HTTPS)

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone and configure

```bash
git clone <repo-url> /opt/persocart
cd /opt/persocart

cp .env.example .env
```

Edit `.env` with production values:

```bash
# Generate a strong secret key:
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<generated-above>
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com

POSTGRES_DB=persocart
POSTGRES_USER=persocart
POSTGRES_PASSWORD=<strong-password>

# Optional: expose on a non-standard port
# PORT=8080
```

### 3. Build and start

```bash
make build-prod
make prod-migrate
make prod-up
```

Check everything is running:

```bash
docker compose -f docker-compose.prod.yml ps
curl http://localhost/healthz/
```

### 4. Create an operator account

```bash
docker compose -f docker-compose.prod.yml run --rm backend \
  python manage.py createsuperuser
```

### 5. HTTPS

Caddy in this setup serves plain HTTP (`auto_https off`) — TLS is terminated upstream. Choose one option:

**Option A — CloudFlare (recommended for most deployments)**

Point your domain to the server via CloudFlare, enable the CloudFlare proxy (orange cloud), and set SSL/TLS mode to "Full". CloudFlare handles the certificate; Caddy receives plain HTTP from the CloudFlare edge.

```bash
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

**Option B — nginx reverse proxy with Certbot**

```bash
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Configure nginx to proxy `http://localhost:80` after obtaining the certificate.

**Option C — Change the exposed port and use a cloud load balancer**

Most cloud providers (AWS ALB, GCP Load Balancing, DigitalOcean load balancer) support TLS termination with managed certificates. Point them at port 80 on this server.

> `SITE_ADDRESS` controls what address Caddy binds to (default: `0.0.0.0:80`). There is no need to change it for any of these options.

---

## Updates

```bash
git pull
make build-prod
make prod-migrate
make prod-down && make prod-up
```

---

## Database Backup & Restore

**Backup:**

```bash
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U persocart persocart > backup-$(date +%Y%m%d).sql
```

**Restore:**

```bash
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U persocart persocart < backup-20240101.sql
```

---

## Maintenance

```bash
make prod-logs          # Follow all logs
make prod-down          # Stop stack (keeps volumes)

# Shell into backend
docker compose -f docker-compose.prod.yml run --rm backend bash

# Seed demo data
docker compose -f docker-compose.prod.yml run --rm backend \
  python manage.py seed_data --products 2000
```

---

## GitHub Container Registry (CI/CD)

On every push to `main`, `.github/workflows/deploy.yml` builds and pushes images to GHCR:

```
ghcr.io/<owner>/persocart/backend:latest
ghcr.io/<owner>/persocart/frontend:latest
```

To pull and run from GHCR instead of building locally, replace the `build:` sections in `docker-compose.prod.yml` with `image:` references:

```yaml
backend:
  image: ghcr.io/<owner>/persocart/backend:latest
frontend:
  image: ghcr.io/<owner>/persocart/frontend:latest
```

Then run:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## Health Checks

| Endpoint | Expected | Description |
|---|---|---|
| `GET /healthz/` | `{"status":"ok"}` | Django liveness probe |

Both the Docker HEALTHCHECK directive and the CI E2E suite hit this endpoint.

---

## Monitoring (optional)

Basic uptime monitoring: point UptimeRobot or Healthchecks.io at `https://your-domain.com/healthz/`.

For metrics, add Prometheus + Grafana to `docker-compose.prod.yml` or use a hosted service.
