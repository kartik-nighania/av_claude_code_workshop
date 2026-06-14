---
name: backend-baseline-security
description: Initial security posture of the TODO backend before hardening
metadata:
  type: project
---

# Backend Security Baseline (2026-06-13)

This is the initial security assessment of the TODO backend. Key findings:

## Critical Issues Found
1. **CORS wide-open** — any origin can make requests
2. **No request size limits** — vulnerable to DoS via large payloads
3. **Error details leaked** — stack traces and messages exposed to clients
4. **No authentication/authorization** — all todos are global, readable/writable by anyone

## Architecture Notes
- Strict layering: routes → controllers → services → store
- Typed errors with `.status` field mapped by error middleware
- In-memory store (swappable for Postgres/SQLite)
- No middleware for auth, rate limiting, or security headers

## How to Apply When Making Changes
When adding new endpoints or modifying error handling:
- Always validate CORS is restricted by origin (don't use bare `cors()`)
- Set explicit payload limits on parsers
- Never expose full errors to clients; log details server-side with error IDs
- Add auth/authz checks in the service layer before allowing operations
- Assume no user isolation — todos currently belong to no one (global)
