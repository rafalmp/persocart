# ADR-005: Per-Category Filter Data Model

## Status
Accepted

## Date
2026-06-14

## Context
The core value is per-category custom filtering. Each category defines its own filters of
varying types (choice, multichoice, number, boolean), and products carry values for their
category's filters. Shoppers apply multiple filters at once, expecting AND-across-filters
(and OR-within a multichoice filter). The open question from PRD §8 was how to model these
values for both flexibility and acceptable multi-filter query performance.

## Decision
We will keep the **typed EAV model** (`ProductFilterValue` with `option` / `value_number` /
`value_boolean` columns) and rely on **careful indexing and query design**, rather than
introducing a denormalized JSONB column for MVP.

Multi-filter queries are composed as an AND of per-filter conditions (each filter resolved
against `ProductFilterValue` rows), using `django-filter` to translate query params into
ORM filters. Indexes: `(product, filter)`, `(filter, option)`, `(filter, value_number)`.

We will **validate** this with a seed dataset at the upper product bound (low-thousands) and
a realistic filter count, asserting query latency targets in the test plan.

## Consequences

### Positive
- Fully flexible: operators add arbitrary filters/options with no schema changes.
- Relational integrity (options are real rows; values reference them).
- Simple mental model; no denormalization sync to maintain.

### Negative
- Multi-filter queries require one join/subquery per applied filter.
- Query construction is more involved than filtering flat columns.

### Risks
- **Risk:** Many simultaneously-applied filters slow queries.
  **Mitigation:** the target scale (low-thousands products, ~10 concurrent users) is small;
  indexes above cover the access patterns; if a real catalog proves slow, add a denormalized
  JSONB `filter_values` column on `Product` with a GIN index as a documented follow-up
  (the EAV stays the source of truth).

## Alternatives Considered
1. **JSONB-only on Product**: Rejected for MVP — loses referential integrity for options and
   complicates validation; kept as a future performance escalation path.
2. **EAV + JSONB hybrid from day one**: Rejected for MVP — premature optimization and sync
   complexity for a scale that indexed EAV handles.
3. **One column per filter (wide table)**: Rejected — impossible with operator-defined,
   per-category dynamic filters.
