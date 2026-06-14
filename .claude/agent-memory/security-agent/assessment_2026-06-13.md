---
name: security-assessment-2026-06-13
description: Detailed security assessment of TODO backend identifying 11 findings across auth, CORS, DoS, data exposure, and input validation
metadata:
  type: project
---

# Security Assessment Summary — 2026-06-13

## Overview
Full code review of `/backend/src/` completed. 11 findings identified, 2 critical, 4 high, 5 medium.

## Critical Issues (Fix Immediately)

1. **CORS wide-open** (backend/src/app.js:11)
   - Bare `cors()` allows any origin to make requests
   - Enables CSRF, cross-origin data theft
   - Fix: whitelist origins via env var or hardcode localhost:5173

2. **No authentication/authorization** (backend/src/services/todoService.js:35)
   - Any client can read, create, update, delete all todos
   - No user concept in data model
   - No ownership enforcement
   - Fix: implement JWT/OAuth + add userId to model + authz checks in services

## High Severity (Fix Before Production)

1. **Error exposure & logging** (backend/src/app.js:24-27)
   - Full stack traces logged to console (console.error)
   - Error messages returned to clients verbatim
   - Leaks file paths, function names, internal state
   - Fix: use error IDs server-side, generic messages to clients

2. **No request size limits** (backend/src/app.js:12)
   - Express JSON parser uncapped → memory exhaustion DoS
   - Title validation (280 chars) happens after parsing, not before
   - Fix: app.use(express.json({ limit: '10kb' }))

3. **Missing security headers** (backend/src/app.js:8)
   - No X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security
   - Vulnerable to MIME-sniffing, clickjacking, HSTS bypass
   - Fix: add helmet middleware or set headers manually

## Key Patterns to Watch

- **Layering discipline**: routes→controllers→services→store is clean; maintain this when adding auth
- **Error mapping**: services throw typed errors with `.status`; error handler in app.js respects this
- **Validation location**: title validation happens correctly in services, not controllers
- **In-memory store**: currently plaintext, no audit trail; will need logging + userId before production

## How to Apply When Adding Features

1. **Auth feature**: Add authentication middleware that extracts user ID and attaches to req; validate user ownership in service layer before returning/modifying todos
2. **New endpoints**: Always set CORS origin, request limits, and security headers at app.js level
3. **Error handling**: Never expose error.message directly; use error IDs + server-side logging
4. **Enumeration risk**: Any endpoint with ID in URL needs rate limiting + ownership checks to prevent dataset enumeration
