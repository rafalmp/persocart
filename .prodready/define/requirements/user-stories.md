# User Stories

Priority key: **P0** = must have for MVP · **P1** = should have for MVP · **P2** = future.
Estimate key: **S** = small · **M** = medium · **L** = large.

---

## Epic 1: Operator Authentication

### US-001: Operator login
**As an** operator
**I want to** log into the admin interface with my email and password
**So that** only I can manage my store's catalog

**Acceptance Criteria**:
- [ ] Given a registered operator, when they submit a correct email + password, then they are authenticated and reach the admin dashboard.
- [ ] Given a registered operator, when they submit an incorrect password, then login is rejected with a generic error (no indication of which field was wrong).
- [ ] Given any login attempt, when the password is stored, then it is hashed with Argon2 (never stored in plaintext).
- [ ] Given a new password, when it is set, then it must be 12–64 characters and pass Django's built-in validators.

**Priority**: P0 · **Estimate**: M

### US-002: Operator logout & session protection
**As an** operator
**I want to** log out and have admin pages protected
**So that** my store cannot be managed by unauthenticated users

**Acceptance Criteria**:
- [ ] Given a logged-in operator, when they click logout, then their session ends and admin pages redirect to login.
- [ ] Given an unauthenticated request to any admin/management endpoint, when it is received, then it is rejected (401/redirect).

**Priority**: P0 · **Estimate**: S

---

## Epic 2: Category Management

### US-003: Create nested categories
**As an** operator
**I want to** create categories and subcategories of arbitrary depth
**So that** I can organize my products into a meaningful tree

**Acceptance Criteria**:
- [ ] Given the admin UI, when the operator creates a category with a name and optional parent, then it appears in the category tree under the chosen parent.
- [ ] Given a category, when it is created without a parent, then it becomes a root (top-level) category.
- [ ] Given a new category, when saved, then a unique URL slug is generated.

**Priority**: P0 · **Estimate**: M

### US-004: Edit, reorder, and delete categories
**As an** operator
**I want to** rename, move, and delete categories
**So that** I can restructure my catalog as the business changes

**Acceptance Criteria**:
- [ ] Given an existing category, when the operator renames it, then the new name is reflected in admin and storefront.
- [ ] Given a category with a parent, when the operator moves it under a different parent, then the subtree moves with it.
- [ ] Given a category that contains products or subcategories, when the operator attempts to delete it, then they are warned and must confirm the cascade.

**Priority**: P1 · **Estimate**: M

---

## Epic 3: Product Management

### US-005: Create and edit products
**As an** operator
**I want to** add products to a category with a name, description, price, and one image
**So that** shoppers can browse my catalog

**Acceptance Criteria**:
- [ ] Given a category, when the operator creates a product with name, price, and (optionally) description and image, then it appears in that category's product list.
- [ ] Given a product, when an image is uploaded, then exactly one image is stored and displayed for that product.
- [ ] Given a product price, when saved, then it is stored as a decimal and rejected if negative or non-numeric.
- [ ] Given an existing product, when the operator edits any field, then the change is persisted and reflected on the storefront.

**Priority**: P0 · **Estimate**: M

### US-006: Delete / deactivate products
**As an** operator
**I want to** remove or hide products
**So that** discontinued items no longer appear to shoppers

**Acceptance Criteria**:
- [ ] Given an existing product, when the operator deletes it, then it no longer appears on the storefront.
- [ ] Given a product, when the operator marks it inactive, then it is hidden from shoppers but retained in admin.

**Priority**: P1 · **Estimate**: S

---

## Epic 4: Custom Filter Management (Core Value)

### US-007: Define per-category filters
**As an** operator
**I want to** define filters specific to a category (e.g. "Heat level" for spices)
**So that** shoppers can narrow products by attributes relevant to that category

**Acceptance Criteria**:
- [ ] Given a category, when the operator adds a filter with a name and type (choice, multi-choice, number, or boolean), then it is associated with that category.
- [ ] Given a choice/multi-choice filter, when the operator adds options (e.g. Mild, Medium, Hot), then those options are available to assign to products.
- [ ] Given a number filter, when defined, then the operator may set an optional unit (e.g. "g", "mm").
- [ ] Given multiple filters on a category, when displayed, then they appear in the operator-defined order.

**Priority**: P0 · **Estimate**: L

### US-008: Assign filter values to products
**As an** operator
**I want to** set each product's value for its category's filters
**So that** the product is matched correctly when shoppers filter

**Acceptance Criteria**:
- [ ] Given a product in a category with filters, when the operator edits the product, then they can set a value for each applicable filter.
- [ ] Given a choice filter, when assigning a value, then only that filter's defined options are selectable.
- [ ] Given a number filter, when assigning a value, then only numeric input is accepted.

**Priority**: P0 · **Estimate**: M

### US-009: Edit and remove filters
**As an** operator
**I want to** rename, reorder, or delete filters and their options
**So that** I can refine my filtering scheme over time

**Acceptance Criteria**:
- [ ] Given an existing filter, when renamed or reordered, then the change is reflected in admin and storefront.
- [ ] Given a filter with assigned product values, when the operator deletes it, then they are warned that product values for it will be removed.

**Priority**: P1 · **Estimate**: M

---

## Epic 5: Storefront Browsing & Filtering (Shopper)

### US-010: Browse the category tree
**As a** shopper
**I want to** navigate the category tree
**So that** I can find the section of products I'm interested in

**Acceptance Criteria**:
- [ ] Given the storefront, when a shopper loads it, then the category tree is displayed and navigable.
- [ ] Given a category, when selected, then the shopper sees the products in that category (and its descendants).
- [ ] Given any viewport (mobile or desktop), when the storefront renders, then the layout is responsive and usable.

**Priority**: P0 · **Estimate**: M

### US-011: Filter products within a category
**As a** shopper
**I want to** apply the filters specific to the selected category
**So that** I can quickly narrow down to the products that match my needs

**Acceptance Criteria**:
- [ ] Given a selected category with defined filters, when the shopper views it, then the category's filters are shown with their available values.
- [ ] Given one or more applied filters, when the shopper applies them, then the product list updates to only products matching all applied filters.
- [ ] Given a multi-choice filter, when several values are selected, then products matching any of the selected values are shown.
- [ ] Given applied filters, when the shopper clears them, then the full category product list returns.

**Priority**: P0 · **Estimate**: L

### US-012: View product detail
**As a** shopper
**I want to** view a product's details and image
**So that** I can evaluate whether it meets my needs

**Acceptance Criteria**:
- [ ] Given a product in the list, when the shopper opens it, then its name, description, price, image, and filter values are shown.
- [ ] Given any viewport, when the product detail renders, then it is responsive and accessible (WCAG).

**Priority**: P0 · **Estimate**: S
