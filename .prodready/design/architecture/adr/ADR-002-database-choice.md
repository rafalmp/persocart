# ADR-002: Database Choice

## Status
Accepted

## Date
2026-06-14

## Context
persocart stores a category tree (MPTT), products, and an EAV-style filter-value model that
must support multi-filter queries efficiently. Deployment is a single self-hosted VPS with
no paid SaaS. PostgreSQL was a fixed requirement from Define; this ADR records why it fits.

## Decision
We will use **PostgreSQL 18** as the single relational database, because:
- Strong relational integrity for the catalog/filter relationships (FKs, unique constraints).
- Excellent, composable indexing (B-tree, partial, and — if needed later — GIN/JSONB) to
  keep multi-filter EAV queries fast at the target scale.
- First-class Django ORM support; trivial to run self-hosted in Docker.
- Mature MPTT support via django-mptt.

## Consequences

### Positive
- Single, well-understood data store; one backup/restore story for the zero-admin model.
- Headroom: full-text search, JSONB, and materialized views available without new infra
  if future features need them.

### Negative
- Requires a persistent volume and a backup routine on the VPS (documented in DEPLOYMENT).
- Vertical-scaling-bound on a single host — acceptable at the stated scale.

### Risks
- **Risk:** EAV multi-filter queries degrade as products grow.
  **Mitigation:** purpose-built indexes on `ProductFilterValue` (see ADR-005); load-test
  with a seed dataset at the upper product bound in the test plan.

## Alternatives Considered
1. **SQLite**: Rejected — fine for dev but weaker concurrency and indexing for the EAV
   query patterns; Postgres is required and worth the small ops cost.
2. **MySQL/MariaDB**: Rejected — Postgres has stronger indexing/JSONB options that give us
   a clean upgrade path for filter performance, and better Django/ecosystem alignment.
3. **A document store (e.g. MongoDB)**: Rejected — the data is highly relational; loses FK
   integrity and migration tooling for no real benefit at this scale.
