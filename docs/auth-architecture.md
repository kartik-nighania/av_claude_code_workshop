# Architecture — JWT + SSO Authentication

> Architect-agent output. Adds JWT-based auth with SSO (OAuth2/OIDC, e.g. Google)
> to the TODO app. Design only — no implementation. Todos become per-user.
> Companion to `docs/architecture.md`.

## Module Structure

### Backend (fits the existing routes → controllers → services → store layering)

```
backend/src/
  app.js                      # (updated) mount authMiddleware + auth routes; requireAuth on todos
  routes/
    todoRoutes.js             # (updated) router.use(requireAuth)
    authRoutes.js             # NEW — /api/auth/* endpoints
  controllers/
    todoController.js         # (updated) reads req.user.id
    authController.js         # NEW — login-url, callback, refresh, me, logout
  services/
    todoService.js            # (updated) every method scoped by userId
    authService.js            # NEW — JWT issue/verify, findOrCreateUser, typed errors
    ssoService.js             # NEW — OIDC provider comms (authz URL, code→token exchange)
  store/
    todoStore.js              # (updated) todos partitioned per user
    userStore.js              # NEW — user persistence (id, email, name, oidcId)
    sessionStore.js           # NEW (optional) — refresh-token revocation tracking
  middleware/
    authMiddleware.js         # NEW — authMiddleware (optional) + requireAuth (gate)
  config/
    sso.js                    # NEW — OIDC provider config
```

### Frontend

```
frontend/src/
  main.jsx                    # (updated) wrap app in <AuthProvider>
  App.jsx                     # (updated) login / callback / protected /app routes
  api.js                      # (updated) attach Bearer token; 401 → refresh → retry
  context/AuthContext.jsx     # NEW — user + isAuthenticated state
  components/
    LoginButton.jsx           # NEW — starts SSO flow
    LogoutButton.jsx          # NEW — clears tokens + redirect
    ProtectedRoute.jsx        # NEW — gatekeeper
    TodoApp.jsx               # NEW — existing todo UI, now protected
```

## Data Model

**User**

| Field          | Type   | Constraints                         |
| -------------- | ------ | ----------------------------------- |
| `id`           | string | UUID, primary key                   |
| `email`        | string | required, unique, lowercased        |
| `name`         | string | optional, from OIDC                 |
| `oidcId`       | string | required, unique (OIDC `sub` claim) |
| `oidcProvider` | string | required (e.g. `"google"`)          |
| `createdAt`    | string | ISO-8601                            |

**Todo (updated)** — adds `userId` (FK → User.id, required); `id` is auto-increment **within a user's scope**.

**JWT shapes**

- **Access token** (~15 min): `{ sub: userId, email, name, iat, exp, iss }`
- **Refresh token** (~7 days): `{ sub: userId, type: "refresh", iat, exp, iss }`

## API Surface

Base: `/api/auth`

| Method | Path         | Request                   | Success                 | Errors           |
| ------ | ------------ | ------------------------- | ----------------------- | ---------------- |
| POST   | `/login-url` | —                         | 200 `{loginUrl, state}` | 500              |
| GET    | `/callback`  | `?code&state`             | 302 → frontend (token)  | 400, 500         |
| POST   | `/refresh`   | `{refreshToken}` / cookie | 200 `{accessToken}`     | 400, 401         |
| GET    | `/me`        | Bearer token              | 200 `User`              | 401              |
| POST   | `/logout`    | `{refreshToken}` / cookie | 204                     | 204 (idempotent) |

**Existing `/api/todos/*`** — unchanged signatures, but all now require `Authorization: Bearer <token>`, operate only on `req.user.id`'s data, and return **403** if a user targets another user's todo, **401** if unauthenticated.

## Data Flows

### Initial SSO login (OIDC authorization-code flow)

```
User → "Login with Google"
  → POST /api/auth/login-url        (backend builds authz URL + random state)
  → frontend stores state in sessionStorage, redirects to Google
  → user consents → Google redirects to /api/auth/callback?code&state
  → backend: verify state (CSRF) → ssoService.exchangeCodeForTokens(code)
           → decode id_token → authService.findOrCreateUser(email, oidcId, name)
           → issue access JWT + refresh token
           → set refresh token (httpOnly cookie), return access token
  → frontend stores access token, user is logged in
```

### Authenticated request

```
GET /api/todos  (Authorization: Bearer <access>)
  → app.js authMiddleware: verify JWT → req.user = {sub,email,name}
  → todoRoutes requireAuth → controller.list(req)
  → service.listTodos(req.user.id) → store.findAllByUserId(userId)
  → 200 with ONLY this user's todos
```

### Token refresh / logout

```
401 on expired access token
  → POST /api/auth/refresh (httpOnly refresh cookie)
  → verify refresh token (+ revocation check) → issue new access token
  → frontend retries original request
  → if refresh also invalid → redirect to /login

Logout → POST /api/auth/logout → revoke refresh token (sessionStore) +
         clear cookie → frontend clears state → /login
```

## External Dependencies

**Backend:** `jsonwebtoken` (sign/verify), `openid-client` (OIDC discovery + code exchange), `dotenv` (secrets). **Frontend:** `react-router-dom` (protected routes).

**Env vars (`.env`, never committed):**

```
JWT_SECRET=...                 JWT_REFRESH_SECRET=...
JWT_EXPIRY=900                 JWT_REFRESH_EXPIRY=604800
GOOGLE_CLIENT_ID=...           GOOGLE_CLIENT_SECRET=...
AUTH_CALLBACK_URL=http://localhost:3001/api/auth/callback
FRONTEND_URL=http://localhost:5173
```

Provider setup: register an OAuth2 web client (Google Cloud Console / Auth0 / Azure AD), set the redirect URI to `AUTH_CALLBACK_URL`, copy client id/secret into `.env`. `ssoService` is provider-agnostic — swap the implementation for other IdPs.

## Error Boundaries

| Failure                                | Layer          | Status | Surfaced as                          |
| -------------------------------------- | -------------- | ------ | ------------------------------------ |
| Missing/invalid OIDC `code`            | authController | 400    | `invalid_grant`                      |
| `state` mismatch (CSRF)                | authController | 400    | `invalid_state` (+ security log)     |
| OIDC provider unreachable              | ssoService     | 500    | `SSO provider unavailable`           |
| Access token missing/expired/malformed | authMiddleware | 401    | `Unauthorized`                       |
| Refresh token expired/revoked          | authService    | 401    | `Refresh token invalid` → re-login   |
| User targets another user's todo       | todoService    | 403    | `Not authorized to access this todo` |
| `JWT_SECRET` missing                   | authService    | 500    | `Server error` (operator fixes cfg)  |

New typed errors (carry `.status`, mapped by `app.js` middleware like the existing ones): `UnauthorizedError` (401), `ForbiddenError` (403), `SsoError` (500).

## Key Design Decisions

- **Token storage:** access token in `localStorage` (short-lived), refresh token in **httpOnly cookie** (`SameSite=Strict`) — balances XSS/CSRF exposure vs. usability.
- **Refresh revocation:** server-side `sessionStore` so logout is a real guarantee and a user's tokens can be mass-revoked.
- **CSRF on callback:** stateless — frontend-generated `state` in `sessionStorage`, validated on return.
- **Middleware order:** global `authMiddleware` is _permissive_ (populates `req.user` if a valid token exists, never rejects), so `/api/auth/*` stays reachable; protected routes add `requireAuth` which rejects with 401 when `req.user` is absent.
- **Store change:** `todoStore` moves from a flat array to a per-user partition (`Map<userId, Todo[]>` + per-user id counter); the service/controller signatures gain a leading `userId`.

## Open Questions

1. Persist to a real DB (User + RefreshToken tables) or keep the in-memory store for the lab?
2. Single provider (Google) or multi-provider (Google + Azure + GitHub) with user de-duplication?
3. Rotate refresh tokens on every refresh (more secure, more revocation bookkeeping) or keep static until expiry?
4. Which OIDC scopes? (`openid profile email` baseline.)
5. Idle-timeout/forced logout, or rely on token expiry alone?
6. Audit logging for failed logins / refresh failures — where to?

## Suggested Implementation Order

1. `authService` + `ssoService` — JWT issue/verify, OIDC code exchange, typed errors.
2. `userStore` — in-memory user persistence (mirrors `todoStore`).
3. `authMiddleware` (`authMiddleware` + `requireAuth`).
4. `authRoutes` + `authController` (login-url, callback, refresh, me, logout).
5. Wire into `app.js`; add `requireAuth` to `todoRoutes`.
6. Thread `userId` through `todoService` / `todoController` / `todoStore` (per-user partition).
7. Frontend `AuthContext` + routing (login → callback → /app → logout).
8. Login/Logout UI components.
9. Update `api.js` — Bearer header, 401→refresh→retry, refresh-failure→login.
10. `config/sso.js` + `.env` documentation.
11. Hand off to the **Test agent** (auth unit/integration tests, todo access-control tests, 401-retry path) and the **Security agent** (token storage, CSRF, OIDC validation, IDOR on todos).
