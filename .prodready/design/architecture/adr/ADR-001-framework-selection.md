# ADR-001: Framework Selection

## Status
Accepted

## Date
2026-06-14

## Context
persocart needs a backend that exposes a REST API to a React SPA, with strong admin,
ORM, auth, and security defaults suited to a zero-admin, GDPR-conscious product built by a
solo developer. Django was a fixed requirement from the Define phase. The REST layer was
initially assumed to be **Tastypie**, but the user was open to a recommendation.

The core value — per-category custom filtering — depends heavily on flexible, well-supported
query/filter tooling.

## Decision
We will use **Django 5.2 LTS** (pinned to the 5.2.x line) with **Django REST Framework
(DRF)** for the API, replacing the Define-phase assumption of Tastypie, because:
- Django 5.2 is the current **LTS** release (supported into 2028); non-LTS 5.0/5.1 are
  already end-of-life, so the LTS line is the right choice for a long-lived self-hosted
  deployment with a solo maintainer.
- DRF is the de facto, actively maintained REST framework for Django; Tastypie is largely
  dormant.
- DRF integrates cleanly with **django-filter**, which directly serves the per-category
  filtering core value.
- DRF's serializers, viewsets, routers, and schema generation speed up solo development and
  keep the API consistent.
- Better documentation and community support reduce risk for a solo developer.

## Consequences

### Positive
- Mature filtering/validation ecosystem aligned with the core value.
- Auto-generated, accurate OpenAPI schema (drf-spectacular) keeps the contract in sync.
- Large hiring/learning/support base.

### Negative
- DRF is heavier than a minimal API layer; some boilerplate (serializers per resource).
- The Define-phase docs referencing Tastypie are now superseded (documented here).

### Risks
- **Risk:** Over-fetching/N+1 queries on nested category/filter data.
  **Mitigation:** `select_related`/`prefetch_related`, explicit serializer design, query
  tests in the test plan.

## Alternatives Considered
1. **Tastypie**: Rejected — minimal recent maintenance, weaker filtering story, smaller
   community; poor long-term fit despite being the original assumption.
2. **Plain Django views + JsonResponse**: Rejected — would reimplement serialization,
   validation, and filtering that DRF provides; slower for a solo dev.
3. **Django Ninja**: Considered — modern and fast, good typing. Rejected for MVP because
   DRF's `django-filter` integration and maturity better fit the filtering-centric core
   value; revisit only if performance demands it.
