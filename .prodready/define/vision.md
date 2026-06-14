# Vision

## Problem Statement
Existing e-commerce platforms and shop software are either too complicated for small,
specialized businesses, or they fail to provide features tailored to specific product
types — most notably, the ability to filter products by category-specific attributes.
Small, specialized businesses (e.g. spice shops, automotive supply stores, jewelry
sellers) need a simple store that can display a tree of categories, show the products in
a selected category, and offer a list of filters specific to that category.

## Target Users

### Shop Operators (primary)
Small, specialized online businesses capable of performing basic administrative tasks
(configuring categories, managing products and filters) through a provided web interface.
The software is **preinstalled** for them — operators perform no OS-level administration,
database setup, or deployment tasks.

### End Shoppers
Assumed to be inexperienced users browsing on either desktop **or** mobile browsers.
**Responsive design is a first-class priority.**

## Core Value Proposition
**Per-category custom filtering.** Operators define filters specific to each category
(e.g. "Heat level" for spices, "Engine type" for auto parts, "Material" for jewelry), and
shoppers can effortlessly narrow the products in a category by those attributes. This is
the single capability the product must do exceptionally well.

## Success Metrics
- **Primary:** % of operators who define at least one custom filter (directly validates
  the core value).
- **Secondary:** operator retention.

## MVP Scope

### Must Have (MVP) — Catalog only, no cart/checkout
- Operator authentication (admin login)
- Category tree management (nested categories)
- Product management (CRUD) within categories
- **Per-category custom filter definitions** (core value)
- One image per product
- Shopper-facing browsing: category tree → product list → apply category-specific filters
- Responsive shopper UI (desktop + mobile)

### Nice to Have (Future)
- Shopping cart + checkout / payments
- Text search
- Multiple product images / media galleries
- Multiple operator/staff accounts per store
- Discounts / promotions
- Analytics dashboard

### Explicit Non-Goals
- **Inventory / stock tracking** (would typically require integration with external software)
- **Multi-site management** (single store per installation)
- Payments / checkout (catalog-only for MVP)
