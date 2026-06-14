# UI Components

Two surfaces share the primitive layer: the **Storefront** (public, responsive, WCAG-first)
and the **Admin** (operator catalog/filter management). All interactive components must be
keyboard-operable, have visible focus, and expose correct ARIA roles/labels.

## Primitives
- [ ] Button (primary, secondary, ghost, danger) — 44px min height, focus ring
- [ ] Input (text, email, password, number) — associated `<label>`, error text via `aria-describedby`
- [ ] Select (native `<select>` preferred for a11y)
- [ ] Checkbox / Checkbox group (multichoice filters)
- [ ] Radio group (single-choice filters)
- [ ] NumberRange (min/max for number filters)
- [ ] Toggle/Switch (boolean filters) — with text label, not color-only

## Composite
- [ ] Form (label/field/error pattern, inline validation)
- [ ] Card (product card: image, name, price)
- [ ] Modal/Dialog (focus trap, ESC to close, `role="dialog"`, labelled) — used for delete confirmations
- [ ] Toast (polite `aria-live` region)
- [ ] Table (admin lists: products, filters)
- [ ] Pagination (accessible prev/next, current-page state)
- [ ] ConfirmDialog (cascade-delete warnings for categories/filters)

## Domain components

### Storefront
- [ ] CategoryTree (collapsible, keyboard-navigable; `aria-expanded`)
- [ ] FilterPanel (renders a category's filters by type; collapsible drawer on mobile)
- [ ] ActiveFilterChips (show + clear applied filters)
- [ ] ProductGrid (responsive grid; empty state when filters match nothing)
- [ ] ProductDetail (image with required alt text, price, description, filter values)
- [ ] Breadcrumbs (category path)

### Admin
- [ ] CategoryTreeEditor (create/rename/move/delete; drag or move-to control)
- [ ] ProductForm (fields + single image upload with alt-text input)
- [ ] FilterEditor (define filter type, options, unit, ordering)
- [ ] ProductFilterValueEditor (set a product's value per applicable filter)

## Layout
- [ ] Header (storefront: store name + nav; admin: account/logout)
- [ ] Sidebar (admin navigation; storefront filter drawer)
- [ ] Footer
- [ ] Container (max-width, responsive padding)
- [ ] SkipToContent link (a11y)

## Accessibility checklist (applies to every component)
- [ ] Reachable and operable by keyboard alone
- [ ] Visible focus indicator
- [ ] Sufficient color contrast (see tokens.md)
- [ ] Labels/roles for assistive tech; images have alt text
- [ ] Works at 320px width and at 200% zoom
