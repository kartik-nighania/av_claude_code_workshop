---
name: frontend-security-posture
description: Frontend (React+Vite) security review findings and posture as of 2026-06-13 — XSS-clean, CSRF/auth/CSP gaps
metadata:
  type: project
---

# Frontend Security Posture — 2026-06-13

Reviewed `/frontend/` (React 18 + Vite, ESM). Small TODO SPA. 4 findings (1 high, 3 low).

## Key facts
- **No XSS sinks.** No `dangerouslySetInnerHTML` anywhere. Todo titles render via auto-escaped JSX (`{todo.title}` in TodoItem.jsx, `{error}` in App.jsx). Do not flag these as XSS.
- **No client tokens/secrets.** No auth on client (matches backend — no auth exists). No localStorage/sessionStorage use. No API keys in client code.
- **FE-001 (high):** mutating requests in api.js (POST/PATCH/DELETE) carry no CSRF token. Exploitable because backend CORS is wide-open + no auth (see [[security-assessment-2026-06-13]] backend findings). This is the only non-forward-looking frontend issue.
- **FE-002/003/004 (low):** forward-looking — no token-storage guardrail, no CSP in index.html, no client-side max-length on title input (backend caps at 280 post-parse).

## How to apply
- When auth is added: push for HttpOnly+SameSite cookies, not Web Storage; add Authorization header in api.js wrapper.
- CSP belongs at the hosting/proxy layer (Vite output is static), not necessarily a meta tag.
- Server remains authoritative validator; client length checks are defense-in-depth only.
