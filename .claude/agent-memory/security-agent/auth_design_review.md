---
name: auth-design-review
description: Security review of the JWT+OIDC auth DESIGN docs (not yet implemented) as of 2026-06-13 — token storage, OIDC, CSRF, IDOR concerns
metadata:
  type: project
---

# Auth Design Review — 2026-06-13 (design-stage, not implemented)

Reviewed `docs/auth-architecture.md` + the "Frontend Auth Changes" section appended to `docs/architecture.md`. These are Architect-agent design docs; no auth code exists yet (backend/frontend source unchanged from baseline — still no auth, CORS wide-open). The lab explicitly hands OIDC/JWT design to the Security agent (auth-architecture.md line 181).

## Design-level concerns to flag when this gets implemented

- **Access token in localStorage** (architecture.md ~L148/L449, auth-architecture.md L154): design rationalizes "ok for XSS" — it is NOT. Any XSS exfiltrates the bearer token. Combined with FE-003 (no CSP) this is a real exposure. Push for in-memory access token + httpOnly refresh cookie.
- **Refresh cookie SameSite**: architecture.md L154 says SameSite=Strict (good); the other doc says "SameSite-protected" loosely. Ensure Strict/Lax + Secure + httpOnly actually set on implementation.
- **OIDC validation gaps**: design says "decode id_token" — must VERIFY signature (JWKS), iss, aud, exp, nonce, not just decode. Easy to get wrong.
- **state CSRF token in sessionStorage** generated client-side: acceptable for OIDC state, but the value must be cryptographically random and compared with constant-time/exact match server-side. Backend should also bind state server-side ideally.
- **No token rotation decision** (open question 3): recommend rotating refresh tokens + revocation via sessionStore (already designed).
- **JWT_SECRET / GOOGLE_CLIENT_SECRET** in `.env` — `.gitignore` already ignores `.env` (verified 2026-06-13). Good. Ensure no fallback default secret in code (no `process.env.JWT_SECRET || 'dev'`).
- **CORS still wide-open** in app.js — once cookies/auth added, bare cors() + credentials is dangerous. The existing critical CORS finding becomes more severe with auth.
- **IDOR**: design correctly scopes todos by req.user.id and returns 403 cross-user (auth-architecture.md L81). Verify the implementation actually enforces ownership in the service layer, not just filters lists.

## Status of implemented code
Backend/frontend source UNCHANGED since baseline. The 15 findings in docs/security_findings.json (11 backend + FE-001..004) all still stand. Do not re-derive; reuse.
