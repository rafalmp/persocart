# Constitution

## Non-Negotiables
- **Responsive design** — storefront must work well on both desktop and mobile browsers.
- **GDPR compliance** — lawful handling of any personal data (operators and shoppers).
- **WCAG accessibility** — storefront must meet accessibility standards for inexperienced
  and assistive-technology users.
- **Zero-admin operator experience** — operators perform no OS-level administration,
  database setup, or deployment. All management happens through the web interface; the
  software is preinstalled.

## Explicit Non-Goals
- **Inventory / stock tracking** (would typically require integration with external software).
- **Multi-site management** (single store per installation).
- **Payments / checkout** (catalog-only for MVP).
- **Invoicing.**

## Technical Constraints
- **Backend:** Python + Django + Tastypie (REST API).
- **Category tree:** `django-mptt` (Modified Preorder Tree Traversal) for arbitrary-depth
  nested categories.
- **Database:** PostgreSQL.
- **Frontend:** React + Bun.
- **Deployment:** Dockerized, deployed on a VPS (minimum 2 vCPU / 4 GB RAM / 40 GB SSD).

## Timeline & Resources
- Timeline: No hard deadline.
- Team: Solo developer.
- Constraints: Single-developer bandwidth — scope kept deliberately tight (catalog-only MVP).
