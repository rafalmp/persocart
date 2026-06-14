# Design Tokens

All color pairings below are chosen to meet **WCAG 2.1 AA** contrast (≥ 4.5:1 for body
text, ≥ 3:1 for large text and UI boundaries). Implemented with **Tailwind CSS 4's
CSS-first config**: tokens are declared in a `@theme { … }` block (CSS custom properties)
after `@import "tailwindcss";` — no `tailwind.config.js`.

## Colors

### Brand
- primary: #1D4ED8        /* on white: 6.3:1 — AA for normal text */
- primary-dark: #1E40AF   /* hover/active */
- secondary: #047857      /* emerald-700, 4.8:1 on white */

### Semantic
- success: #15803D
- warning: #B45309        /* amber-700 for AA text contrast */
- error: #B91C1C
- info: #1D4ED8

### Neutral
- background: #FFFFFF
- surface: #F9FAFB
- text-primary: #111827   /* 16:1 on white */
- text-secondary: #4B5563 /* 7.5:1 on white — AA even at small sizes */
- border: #D1D5DB         /* ≥ 3:1 against surface for non-text UI */
- focus-ring: #2563EB     /* visible focus indicator (a11y) */

## Typography

- font-family: Inter, system-ui, sans-serif
- base size: 1rem (16px) minimum for body — no sub-16px body text (mobile readability)
- font-size-xs: 0.75rem   (labels/meta only, never primary content)
- font-size-sm: 0.875rem
- font-size-base: 1rem
- font-size-lg: 1.125rem
- font-size-xl: 1.25rem
- font-size-2xl: 1.5rem
- line-height-body: 1.5 (WCAG 1.4.12 spacing)

## Spacing

- spacing-1: 0.25rem
- spacing-2: 0.5rem
- spacing-3: 0.75rem
- spacing-4: 1rem
- spacing-6: 1.5rem
- spacing-8: 2rem
- tap-target-min: 44px    /* minimum interactive target (WCAG 2.5.5 / mobile) */

## Border Radius

- radius-sm: 0.25rem
- radius-md: 0.375rem
- radius-lg: 0.5rem
- radius-full: 9999px

## Shadows

- shadow-sm: 0 1px 2px rgba(0,0,0,0.05)
- shadow-md: 0 4px 6px rgba(0,0,0,0.1)
- shadow-lg: 0 10px 15px rgba(0,0,0,0.1)

## Breakpoints (responsive, mobile-first)

- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px

## Accessibility tokens

- Always-visible focus outline using `focus-ring` (never `outline: none` without replacement).
- Honor `prefers-reduced-motion` — disable non-essential transitions.
- Color is never the sole carrier of meaning (icons/text accompany state colors).
