# Data Model

The model centers on the core value: **per-category custom filtering**. Categories form an
arbitrary-depth tree (managed by `django-mptt`). Each category can define its own filters;
each product carries values for the filters of its category.

## Entities

### Operator (custom User)
Email-based authentication; no username field.
- id: BigInt (PK)
- email: String (unique, login identifier)
- password: String (Argon2 hash; 12–64 char policy enforced at form/serializer)
- is_active: Boolean
- is_staff: Boolean
- is_superuser: Boolean
- date_joined: DateTime
- last_login: DateTime (nullable)

### Category (MPTT node)
- id: BigInt (PK)
- name: String
- slug: String (unique, URL identifier)
- parent: FK → Category (nullable; null = root)
- lft, rght, tree_id, level: Integer (managed by django-mptt)
- created_at: DateTime
- updated_at: DateTime

### Product
- id: BigInt (PK)
- category: FK → Category
- name: String
- slug: String (unique within store)
- description: Text (nullable)
- price: Decimal(10,2) (>= 0)
- image: Image/File path (nullable; one image per product)
- is_active: Boolean (hidden from storefront when false)
- created_at: DateTime
- updated_at: DateTime

### CategoryFilter (filter definition — the core value)
- id: BigInt (PK)
- category: FK → Category
- name: String (e.g. "Heat level")
- slug: String (unique within category)
- type: Enum { choice, multichoice, number, boolean }
- unit: String (nullable; e.g. "g", "mm" — meaningful for number filters)
- position: Integer (display order)
- created_at: DateTime
- updated_at: DateTime

### CategoryFilterOption (allowed values for choice / multichoice filters)
- id: BigInt (PK)
- filter: FK → CategoryFilter
- label: String (e.g. "Hot")
- value: String (normalized/stored value)
- position: Integer (display order)

### ProductFilterValue (a product's value for one filter)
Typed columns; exactly one is populated depending on the filter's type.
For multichoice, multiple rows reference different options of the same filter.
- id: BigInt (PK)
- product: FK → Product
- filter: FK → CategoryFilter
- option: FK → CategoryFilterOption (nullable; used for choice/multichoice)
- value_number: Decimal (nullable; used for number)
- value_boolean: Boolean (nullable; used for boolean)

## Relationships
- Category 1:N Category (self-referential tree via django-mptt)
- Category 1:N Product
- Category 1:N CategoryFilter
- CategoryFilter 1:N CategoryFilterOption
- Product 1:N ProductFilterValue
- CategoryFilter 1:N ProductFilterValue
- CategoryFilterOption 1:N ProductFilterValue

## Indexes
- Operator.email (unique)
- Category.slug (unique)
- Category (lft, rght, tree_id, level) — MPTT tree indexes
- Product.slug (unique)
- Product.category (FK index, for category product listings)
- Product.is_active (storefront visibility filtering)
- CategoryFilter.category (FK index)
- CategoryFilter (category, slug) — unique together
- ProductFilterValue (product, filter) — lookups when rendering a product
- ProductFilterValue (filter, option) — lookups when filtering a category's products
- ProductFilterValue (filter, value_number) — range/number filtering

## Open Questions
- **Filter inheritance:** MVP assumes filters shown for a category are those defined
  directly on it; products listed include the category and its descendants. Whether
  filters should be inherited from ancestor categories is deferred (see prd.md §8).
