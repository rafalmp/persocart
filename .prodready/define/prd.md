# Product Requirements Document (PRD)

## 1. Executive Summary

**Product**: persocart
**Problem**: Existing e-commerce software is either too complex for small specialized
businesses or lacks product-type-specific features — above all, the ability to filter
products by attributes that matter for a given category.
**Solution**: A simple, preinstalled storefront where operators build a category tree,
manage products, and define **per-category custom filters**; shoppers browse a category
and narrow products by that category's specific filters.
**Target Users**: Small specialized online businesses (spice shops, automotive supply,
jewelry, etc.) as operators; inexperienced shoppers on web and mobile.
**Success Metric**: % of operators who define at least one custom filter (validates the
core value); secondarily, operator retention.

## 2. Goals & Non-Goals

### Goals
- Make per-category custom filtering the standout, effortless capability for both
  operators (defining filters) and shoppers (applying them).
- Let operators manage an arbitrary-depth category tree, products (one image each), and
  filters entirely through a web UI with zero OS/DB/deployment work.
- Deliver a responsive, WCAG-accessible, GDPR-compliant storefront.

### Non-Goals
- No inventory / stock tracking.
- No multi-site management (one store per installation).
- No cart, checkout, or payments in MVP.
- No invoicing.

## 3. User Personas

### Persona 1: Shop Operator
- **Context**: Owner of a small, specialized shop (e.g. a spice merchant). Comfortable
  with basic web admin tasks but not with servers, databases, or deployment.
- **Pain Point**: Mainstream platforms are overwhelming and can't express the
  attribute-based filtering their niche products need.
- **Desired Outcome**: Stand up a clean catalog with category-specific filters quickly,
  with no technical setup.

### Persona 2: End Shopper
- **Context**: Inexperienced user browsing on desktop or mobile.
- **Pain Point**: Struggles to find the right product among many similar items.
- **Desired Outcome**: Pick a category, apply a couple of relevant filters, and reach the
  right products fast.

## 4. Functional Requirements

### FR-1: Operator Authentication
- Email-based login (custom user model, no username); Argon2 hashing; password 12–64 chars
  with Django validators; admin endpoints protected.
- **Acceptance**: Correct credentials reach the dashboard; wrong credentials get a generic
  error; unauthenticated requests to management endpoints are rejected.

### FR-2: Category Management
- Create/edit/move/delete categories of arbitrary depth (django-mptt); auto-generated
  unique slugs; cascade warnings on non-empty deletes.
- **Acceptance**: New categories appear correctly in the tree; moving a node moves its
  subtree.

### FR-3: Product Management
- CRUD products within a category; name, description, price (decimal ≥ 0), one image;
  active/inactive visibility.
- **Acceptance**: Products appear in their category; negative prices rejected; inactive
  products hidden from shoppers.

### FR-4: Per-Category Custom Filters (core)
- Define filters per category with type choice / multichoice / number / boolean; options
  for choice types; optional unit for number; operator-defined ordering. Assign each
  product's values for its category's filters.
- **Acceptance**: Filters attach to the right category; only valid options/numeric values
  are accepted; filter order is honored.

### FR-5: Storefront Browsing & Filtering
- Navigable category tree; product listing for the selected category (and descendants);
  apply/clear that category's filters; multichoice = match-any; responsive product detail
  with image and filter values.
- **Acceptance**: Applying filters narrows the list correctly; clearing restores it;
  layouts are responsive and accessible.

## 5. Non-Functional Requirements

- **Performance**: Comfortable on a 2 vCPU / 4 GB / 40 GB VPS for hundreds–low-thousands
  of products and up to ~10 concurrent shoppers.
- **Security**: GDPR (minimal personal data — anonymous shoppers, operator accounts only);
  Argon2; protected admin; TLS terminated at a reverse proxy.
- **Accessibility**: Storefront meets WCAG.
- **Availability/Ops**: Fully containerized (Docker), self-hosted, no paid SaaS; zero-admin
  for operators (preinstalled).
- **Budget**: Free/open-source tooling only.

## 6. Data Model Summary

### Entities
- **Operator**: email-based custom user (admin).
- **Category**: MPTT tree node (name, slug, parent) — arbitrary depth.
- **Product**: belongs to a category; name, description, price, single image, active flag.
- **CategoryFilter**: a category's filter definition (name, type, optional unit, order).
- **CategoryFilterOption**: allowed values for choice/multichoice filters.
- **ProductFilterValue**: a product's value for one filter (option, number, or boolean).

### Key Relationships
- Category → Category: self-referential tree (django-mptt).
- Category → Product / CategoryFilter: a category owns its products and its filters.
- Product → ProductFilterValue ← CategoryFilter: products carry typed values for their
  category's filters (multichoice = multiple rows).

## 7. Scope & Timeline

- **MVP Features**: operator auth; category tree management; product CRUD with one image;
  per-category custom filters and product value assignment; responsive, accessible
  storefront browsing and filtering. Catalog-only (no cart).
- **Future Features**: cart + checkout + payments; text search; multiple product images;
  multiple operator accounts; discounts/promotions; analytics; shopper accounts; 2FA.
- **Timeline**: No hard deadline.
- **Team**: Solo developer.

## 8. Open Questions & Risks

- **Filter inheritance**: MVP shows only filters defined directly on the selected category
  while listing products from it and its descendants. Whether ancestor-defined filters
  should apply to descendant products needs validation with real catalogs.
- **Filtering performance**: The typed EAV-style `ProductFilterValue` model is flexible but
  requires careful indexing/query design for multi-filter queries; validate against the
  upper product range.
- **Image handling**: Single-image storage, resizing/thumbnails, and accessible alt text
  to be specified in Design (impacts WCAG and mobile performance).
- **GDPR specifics**: Even with anonymous shoppers, cookie/consent and operator data
  handling details to be confirmed in Design.

## 9. References

- Detailed user stories: `requirements/user-stories.md`
- Data model details: `data-model/entities.md`, `data-model/models.py`
- Test scenarios: `test-scenarios/*.feature`
- Vision: `vision.md` · Constitution: `constitution.md` · Constraints: `constraints.md`
