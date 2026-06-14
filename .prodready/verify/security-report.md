# Security Audit Report

Generated: 2026-06-14

## Dependency Scan

### Backend (pip-audit)

```
Found 1 known vulnerability in 1 package
Name   Version ID             Fix Versions
------ ------- -------------- ------------
pytest 8.4.2   CVE-2025-71176 9.0.3
```

| Severity | Count | Notes |
|----------|-------|-------|
| Critical | 0 | — |
| High | 0 | — |
| Medium | 0 | — |
| Low | 1 | pytest (dev-only, not in production image) |

**Note**: pytest is listed in `requirements-dev.txt` only and is NOT installed in the production Docker image (`runtime` stage installs `requirements.txt` exclusively). No production exposure.

### Frontend (bun audit)

```
No vulnerabilities found
```

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |

## Secrets Detection

Manual scan of repository — no real secrets found:
- `.env` is in `.gitignore`
- `.env.example` contains only placeholder values (`change-me-in-production`, `insecure-dev-key-change-me`)
- CI uses environment variables (`${{ secrets.GITHUB_TOKEN }}`, `ci-secret-key`)
- `DJANGO_SECRET_KEY` is read from environment at runtime

## OWASP Top 10 Checklist

| # | Vulnerability | Status | Notes |
|---|---------------|--------|-------|
| A01 | Broken Access Control | ✓ Pass | `IsAuthenticated` on all admin endpoints; storefront is read-only public |
| A02 | Cryptographic Failures | ✓ Pass | Argon2 password hashing (argon2-cffi); session cookie `Secure=True`, `HttpOnly=True` in production |
| A03 | Injection | ✓ Pass | Django ORM with parameterized queries throughout; no raw SQL |
| A04 | Insecure Design | ✓ Pass | Session-based auth (ADR-003); no JWT secret storage risk |
| A05 | Security Misconfiguration | ✓ Pass | `DEBUG=False` in production; `ALLOWED_HOSTS` required; `CSRF_COOKIE_SECURE=True` when not debug |
| A06 | Vulnerable Components | ✓ Pass | No critical/high CVEs; only dev-only pytest low CVE |
| A07 | Auth Failures | ⚠ Note | No rate limiting on `/auth/login` — acceptable for MVP operator-only admin; recommended for future |
| A08 | Data Integrity Failures | ✓ Pass | DRF serializer validation on all write endpoints; CSRF enforced |
| A09 | Logging Failures | ✓ Pass | No PII logged; gunicorn access log with `--access-logfile -` (stdout) |
| A10 | SSRF | ✓ Pass | No external URL fetching by the application |

## Code Review Checklist

- [x] No hardcoded secrets in source code
- [x] Passwords hashed with Argon2 (not bcrypt/MD5/plaintext)
- [x] Secret key loaded from environment variable
- [x] All write inputs validated through DRF serializers
- [x] CSRF protection enabled (`CsrfViewMiddleware` in MIDDLEWARE)
- [x] Session cookies: `HttpOnly=True`, `SameSite=Lax`, `Secure=True` in production
- [x] `DJANGO_DEBUG=false` enforced in production compose
- [x] Media files served separately (not through Django in production)
- [x] Non-root user in production Docker images (`USER app`)
- [x] Error responses do not leak internal stack traces in production

## Issues Found

| Severity | Issue | Recommendation |
|----------|-------|----------------|
| Low | `pytest 8.4.2` CVE-2025-71176 | Upgrade to `pytest>=9.0.3` in requirements-dev.txt. Dev-only, no production impact. |
| Info | No rate limiting on login endpoint | Add `AnonRateThrottle` to `LoginView` before exposing to public internet |

## Result

**Status: PASSED — 0 Critical, 0 High issues**

- Critical: 0
- High: 0
- Medium: 0
- Low: 1 (dev-only dependency, no production exposure)
