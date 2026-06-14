# ADR-003: Authentication Strategy

## Status
Accepted

## Date
2026-06-14

## Context
Only **operators** authenticate; **shoppers are anonymous** in MVP. The admin is a
first-party React SPA served from the same origin as the API (behind one reverse proxy).
Constraints require Argon2 hashing, a 12–64 character password policy, GDPR-minimal data,
and TLS terminated at the proxy. 2FA is explicitly out of scope for MVP but should be
addable later.

## Decision
We will use **session-based cookie authentication** (DRF `SessionAuthentication` over
Django's session framework) for operators, because:
- The SPA and API share an origin, so cookies are the simplest secure transport — no token
  storage in JS, avoiding XSS token-theft risks.
- Server-side sessions support immediate revocation (logout/forced logout) — relevant to
  GDPR and account security.
- Plays directly with Django's auth, CSRF protection, and the future 2FA path
  (e.g. django-otp) without re-architecting.

Cookie settings: `HttpOnly`, `Secure`, `SameSite=Lax`. CSRF protection enabled for unsafe
methods. Passwords hashed with Argon2 (`argon2-cffi`) as the primary hasher; 12–64 char
policy enforced via Django validators + a custom length validator.

## Consequences

### Positive
- No client-side token handling; smaller XSS attack surface.
- Built-in revocation and Django CSRF integration.
- Clean upgrade path to 2FA and, later, shopper accounts.

### Negative
- Requires CSRF token handling in the SPA for write requests.
- Sessions are server-side state (stored in Postgres/cache) — negligible at this scale.

### Risks
- **Risk:** CSRF misconfiguration on the SPA.
  **Mitigation:** standard Django CSRF cookie + `X-CSRFToken` header pattern; covered by
  E2E tests for login and a protected write.
- **Risk:** Cookie/session handling across proxy.
  **Mitigation:** same-origin deployment via Caddy; document proxy headers in DEPLOYMENT.

## Alternatives Considered
1. **JWT in localStorage**: Rejected — XSS token theft risk, awkward revocation, no benefit
   for a same-origin first-party SPA.
2. **JWT in HttpOnly cookie**: Rejected — adds token rotation/blacklist complexity over
   Django sessions with little gain at this scale.
3. **OAuth/social login**: Rejected for MVP — operators are a small known set; unnecessary
   third-party dependency (and no paid SaaS).
