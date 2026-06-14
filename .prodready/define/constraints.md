# Constraints

## Deployment
- Target: VPS (single host), Dockerized.
- Minimum spec: 2 vCPU / 4 GB RAM / 40 GB SSD.
- TLS/HTTPS: terminated at a reverse proxy in front of the application (not handled by
  the app itself).

## Scale
- Products: hundreds to low thousands per store.
- Concurrency: up to ~10 concurrent shoppers.
- Launch and 6-month projections are within the same modest range (no aggressive growth
  assumptions); the VPS spec comfortably covers it.

## Budget
- Infrastructure: self-hosted in Docker, no paid SaaS.
- Tooling: free / open-source only.

## Compliance & Security
- **GDPR** compliance (minimal personal data: anonymous shoppers in MVP; operator
  accounts only).
- **WCAG** accessibility for the storefront.
- **Authentication:** custom Django user model using **email** instead of username.
- **Password hashing:** Argon2.
- **Password policy:** Django built-in validators; length **12–64 characters**.
- **2FA:** nice to have, **out of scope for MVP**.
- **Shopper accounts:** anonymous in MVP; accounts deferred to a later version.

## Tech Stack Preferences
- Language: Python (backend), JavaScript/TypeScript (frontend).
- Backend framework: Django + Tastypie (REST API).
- Category tree: `django-mptt` (Modified Preorder Tree Traversal).
- Database: PostgreSQL.
- ORM: Django ORM.
- Frontend: React, built/run with Bun.
- Additional: fully containerized; deployed behind a reverse proxy on a VPS.
