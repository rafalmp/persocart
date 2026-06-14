# ADR-004: Architecture Pattern

## Status
Accepted

## Date
2026-06-14

## Context
Solo developer, no hard deadline, single VPS, modest scale (~10 concurrent shoppers,
hundreds–low-thousands of products). The user explicitly prioritized **managing long-term
complexity** so future features (cart, search, shopper accounts) can be added cleanly.

## Decision
We will build a **modular monolith**: one deployable Django backend organized into bounded
Django apps (`accounts`, `catalog`, `filters`, `storefront`, `api`), with a separate React
SPA client. See `pattern.md` for the full structure.

## Consequences

### Positive
- Trivial ops for a solo dev / zero-admin deploy (one compose stack).
- Clear internal boundaries keep the code maintainable and make future features additive.
- No distributed-systems overhead (network calls, eventual consistency) the scale doesn't need.

### Negative
- Discipline required to keep module boundaries from eroding.
- Single deployable unit — the whole app deploys together (acceptable here).

### Risks
- **Risk:** Boundaries blur over time into a "big ball of mud."
  **Mitigation:** cross-module access via explicit service functions; enforce in review and
  via import-linting if needed.

## Alternatives Considered
1. **Plain monolith (no module discipline)**: Rejected — conflicts with the stated
   long-term-complexity priority.
2. **Microservices**: Rejected — operational overhead unjustified at this scale and team size.
3. **Serverless**: Rejected — self-hosted/no-paid-SaaS constraint and stateful Postgres +
   media volumes make a single host the natural fit.
