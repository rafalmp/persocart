# Gemini Code Assist style guide

Read by Gemini Code Assist on every PR opened in this repository.

## GUARDRAILS prohibitions — enforced as HIGH, no exceptions

These rules are inviolable. Violation blocks merge regardless of PR context.

- **PII as plaintext in DB or logs [HIGH].** Email, IP, phone, full name, payment data stored or logged in plaintext = STOP. Use a hash (for lookup) plus encrypted ciphertext (for retrieval), or column-level encryption.
- **SQL built by string concatenation with user input [HIGH].** Always use parameterized queries (`$1`, `?`, `:name`).
- **Secrets committed to the repo [HIGH].** JWT signing keys, API keys, DB passwords, OAuth client secrets must live in `.env` / a secrets manager, not in tracked files.
- **Any database engine other than PostgreSQL [HIGH].** SQLite, MySQL, MongoDB, DynamoDB are blocked (ADR-002 + constitution).

## What the review must NOT do

**Do not comment on code style.** ESLint, Prettier, and TypeScript strict run earlier. Comments like "use const instead of let", "missing semicolon", "prefer arrow function" are noise.

**Do not rewrite working logic "better".** If the code works and is readable, suggestions like "rewrite to functional style" or "extract to a separate file" are noise. Comment only on a concrete bug or regression.

**Do not repeat comments.** If the same issue appears in five places, leave one comment with the list of locations, not five separate ones.

## Repository conventions

Stack: Python 3.13, Django 5.2, Django Rest Framework 3.17, PostgreSQL 18, React 19, React Router 7, TypeScript strict, Tailwind 4. Modular monolith: `backend/accounts`, `backend/api`, `backend/catalog`, `backend/storefront`.
