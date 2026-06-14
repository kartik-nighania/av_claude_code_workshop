---
name: frontend-auth-design
description: Frontend auth changes needed to align with OAuth2/OIDC architecture; appended to docs/architecture.md
metadata:
  type: project
---

## Frontend Auth Design (2026-06-13)

Completed the "Frontend Auth Changes" section of `/Users/kartik/Documents/analytics_vidhya/docs/architecture.md`, appending a detailed design blueprint for frontend OAuth2/OIDC integration.

**Key deliverables:**

1. Module structure: AuthContext, LoginPage, CallbackPage, ProtectedRoute, TodoApp refactor
2. Auth state management: user, isAuthenticated, isLoading, error in context
3. Token storage design: access token in localStorage, refresh token in httpOnly cookie
4. Data flows: login (OIDC authz code), authenticated request (Bearer + 401 retry), logout
5. API client changes: Bearer header injection, 401→refresh→retry logic, error handling
6. Route structure: /login, /callback, /app (protected), /404
7. Error boundaries and design decisions documented
8. 10-step implementation order provided

**Why:** Architected based on `docs/auth-architecture.md` backend design and current frontend structure (no routing, no auth state, bare api.js client).

**How to apply:** Implementation agents (Test, Security, Reviewer) use this as the contract for evaluating frontend PR changes. Includes all component signatures, state shapes, data flows, and error handling required.
