# Architecture — TODO Service

> This is a sample Architect-agent output, pre-seeded so the lab has a blueprint
> on day 0. In the hands-on session, regenerate or extend it with the Architect
> agent (see `prompts/architect-agent.md`).

## Module Structure

```
backend/
  src/
    server.js              # entry point — binds app to a port
    app.js                 # express wiring + error middleware
    routes/todoRoutes.js   # /api/todos route table
    controllers/           # HTTP layer (req/res → service calls)
      todoController.js
    services/              # business logic + validation (no HTTP here)
      todoService.js
    store/                 # persistence (swappable; in-memory for the demo)
      todoStore.js
  tests/todos.test.js      # integration tests (supertest + jest)

frontend/
  src/
    main.jsx               # React entry
    App.jsx                # state container + data fetching
    api.js                 # fetch client for /api/todos
    components/
      AddTodo.jsx
      TodoList.jsx
      TodoItem.jsx
    styles.css
```

## Data Model

| Field       | Type    | Constraints                          |
| ----------- | ------- | ------------------------------------ |
| `id`        | integer | auto-increment, unique               |
| `title`     | string  | required, trimmed, ≤ 280 chars       |
| `completed` | boolean | defaults to `false`                  |
| `createdAt` | string  | ISO-8601 timestamp, set on insert    |

## API Surface

Base path: `/api/todos`

| Method | Path                | Request body            | Success         | Errors           |
| ------ | ------------------- | ----------------------- | --------------- | ---------------- |
| GET    | `/`                 | —                       | 200 `Todo[]`    | —                |
| POST   | `/`                 | `{ title }`             | 201 `Todo`      | 400              |
| GET    | `/:id`              | —                       | 200 `Todo`      | 400, 404         |
| PUT    | `/:id`              | `{ title?, completed? }`| 200 `Todo`      | 400, 404         |
| PATCH  | `/:id/toggle`       | —                       | 200 `Todo`      | 400, 404         |
| DELETE | `/:id`              | —                       | 204             | 400, 404         |

Plus `GET /health` → `{ status: "ok" }`.

## Data Flows

```
Request → app.js (json parse) → todoRoutes → todoController
        → todoService (validation + rules) → todoStore (persistence)
        → back up the stack → JSON response
Errors thrown in any layer carry `.status` and are mapped by app.js middleware.
```

## External Dependencies

- Backend: `express`, `cors`; dev: `jest`, `supertest`.
- Frontend: `react`, `react-dom`; dev: `vite`, `@vitejs/plugin-react`.
- Env: `PORT` (backend, default 3001). Frontend dev server proxies `/api` → :3001.

## Error Boundaries

| Failure                     | Where         | Surfaced as           |
| --------------------------- | ------------- | --------------------- |
| Missing/blank title         | todoService   | 400 `title is required` |
| Title too long (>280)       | todoService   | 400                   |
| Unknown id                  | todoService   | 404 `Todo not found`  |
| Non-integer id              | todoController| 400 `invalid id`      |
| Unmatched route             | app.js        | 404 `Not found`       |
| Unexpected error            | app.js        | 500 (logged)          |

## Open Questions (for the lab)

- Persistence: swap in-memory store for SQLite/Postgres?
- Auth: do todos belong to a user? (currently global)
- Tags / due dates / priority — candidate features to build with the agent team.

---

# Frontend Auth Changes (aligns with `docs/auth-architecture.md`)

## Overview

The frontend must be refactored to support OAuth2/OIDC single sign-on (Google) and token-based authentication. Key responsibilities:

1. **Auth state management** — where the user's identity, access token, and session live
2. **Login/logout flows** — OAuth2 authorization code dance, token persistence, logout teardown
3. **Route guarding** — redirect unauthenticated users to login
4. **API client enhancement** — attach Bearer tokens, handle 401 refresh-and-retry
5. **Component addition** — login button, logout button, protected route wrapper

## Module Structure

```
frontend/src/
  main.jsx                          # (updated) wrap <App> in <AuthProvider>
  App.jsx                           # (updated) conditional routing: /login | /callback | /app
  api.js                            # (updated) Bearer token attachment; 401→refresh→retry
  context/
    AuthContext.jsx                 # NEW — provides user, isAuthenticated, login, logout, loading
  components/
    LoginButton.jsx                 # NEW — trigger login flow
    LogoutButton.jsx                # NEW — trigger logout + clear state
    ProtectedRoute.jsx              # NEW — component wrapper; redirect if unauthenticated
    TodoApp.jsx                     # REFACTORED from current App.jsx (move todo logic here)
    AddTodo.jsx                     # (unchanged, but now scoped inside <TodoApp />)
    TodoList.jsx                    # (unchanged)
    TodoItem.jsx                    # (unchanged)
  pages/
    LoginPage.jsx                   # NEW — login UI (button + optional branding)
    CallbackPage.jsx                # NEW — handles /callback?code&state after OAuth redirect
    NotFoundPage.jsx                # NEW — 404 fallback
  styles.css                        # (updated) add login/callback page styles
  vite.config.js                    # (no changes needed; already proxies /api → :3001)
```

## Data Model (Frontend Auth State)

**AuthContext state:**

```typescript
{
  user: {
    id: string,           // UUID from JWT
    email: string,        // from JWT
    name: string,         // from JWT (optional)
  } | null,
  isAuthenticated: boolean,  // true if user is logged in
  isLoading: boolean,        // true during login flow or initial auth check
  error: string | null,      // error message (e.g., "Callback failed: invalid_state")
}
```

**Token storage:**
- **Access token** → `localStorage` (`auth:accessToken` key)
- **Refresh token** → httpOnly cookie (set by backend, never readable from JS)
- **State (for CSRF)** → `sessionStorage` (`auth:state` key) during login, cleared after callback

## API Surface Changes

**New `AuthContext` methods:**

- `login()` — initiates OAuth2 flow: fetch `/api/auth/login-url`, store state, redirect to Google
- `handleCallback(code, state)` — called in `/callback` route; exchanges code for tokens
- `logout()` — clears tokens + calls POST `/api/auth/logout`
- `refreshToken()` — internal; exchanges refresh token for new access token

**Updated `api.js` client:**

- Attach `Authorization: Bearer <accessToken>` to all requests (except `/auth/*`)
- On 401 response: call `authContext.refreshToken()`, then retry the original request
- On refresh failure (401): clear tokens, redirect to `/login`
- Catch network/timeout errors; surface them to the caller

## Data Flows

### Login Flow

```
User clicks "Login with Google" (LoginButton)
  ↓
AuthContext.login()
  ↓
POST /api/auth/login-url
  ← { loginUrl, state }
  ↓
Store state in sessionStorage (CSRF token)
  ↓
Redirect to loginUrl (Google OAuth consent screen)
  ↓
User grants permission
  ↓
Google redirects to /callback?code=...&state=...
  ↓
<CallbackPage /> extracts code + state from URL
  ↓
AuthContext.handleCallback(code, state)
  ↓
POST /api/auth/callback?code=<code>&state=<state>
  ← { accessToken }
  ← (refresh token in httpOnly cookie, auto-sent by browser)
  ↓
Store accessToken in localStorage
  ↓
Clear sessionStorage state
  ↓
Set AuthContext.user + isAuthenticated = true
  ↓
Redirect to /app (protected TodoApp)
```

### Authenticated Request with Auto-Refresh

```
User navigates to /app/todos
  ↓
ProtectedRoute checks isAuthenticated; if false → redirect to /login
  ↓
<TodoApp /> calls api.list()
  ↓
api.js attaches Authorization: Bearer <accessToken>
  ↓
GET /api/todos
  ← 200 with user's todos (success path)
  ← OR 401 (expired access token)
  ↓
IF 401:
  POST /api/auth/refresh (httpOnly refresh cookie sent auto)
    ← { accessToken } (new token)
    ← OR 401 (refresh token expired/revoked)
  ↓
  IF refresh succeeded:
    Store new accessToken in localStorage
    ↓
    Retry GET /api/todos with new token
      ← 200 with todos
  ↓
  IF refresh failed:
    Clear localStorage tokens
    ↓
    Set AuthContext.user = null, isAuthenticated = false
    ↓
    Redirect to /login (with optional ?returnTo=/app param)
```

### Logout Flow

```
User clicks "Logout" (LogoutButton)
  ↓
AuthContext.logout()
  ↓
POST /api/auth/logout
  (refresh token sent in httpOnly cookie; backend revokes it)
  ← 204 No Content
  ↓
Clear localStorage (accessToken)
  ↓
Backend clears httpOnly cookie (Set-Cookie: refresh=; Max-Age=0)
  ↓
Set AuthContext.user = null, isAuthenticated = false
  ↓
Redirect to /login
```

## Component Responsibilities

### `AuthContext.jsx`

**Provides:**
- `useAuth()` hook (or context consumer) to access `{ user, isAuthenticated, isLoading, error, login, logout }`
- Manages token lifecycle: fetch, store, refresh, revoke
- Exposes `handleCallback(code, state)` for CallbackPage to call

**State management:**
- `useState(user, isAuthenticated, isLoading, error)`
- Effect: on mount, check if accessToken exists in localStorage; if so, verify it's valid (optional: call `/api/auth/me` to confirm)

**Error handling:**
- Typed errors from backend (e.g., `invalid_state`, `refresh_token_invalid`) are stored in `error` state
- Components can display errors or retry

### `LoginPage.jsx`

**Displays:**
- A login form/screen with a "Login with Google" button
- Optional loading state while redirecting to Google
- Any error messages (e.g., if login-url fetch fails)

**Calls:**
- `authContext.login()` on button click

### `CallbackPage.jsx`

**Purpose:**
- Handles the OAuth2 callback (`/callback?code=...&state=...`)
- Immediately extracts URL params and calls `authContext.handleCallback(code, state)`
- Shows a loading spinner while exchanging code for token
- If callback fails: display error and link back to login
- If successful: redirect to `/app` (happens in AuthContext after storing token)

**Logic:**
- Extract `code` and `state` from URL params
- Call `authContext.handleCallback(code, state)`
- Wait for `isAuthenticated` to become true (or error)
- Redirect to `/app` or show error

### `ProtectedRoute.jsx`

**Purpose:**
- Wraps routes that require authentication (e.g., `<ProtectedRoute component={TodoApp} />`)
- Checks `isAuthenticated`; if false, redirect to `/login` (optionally with `?returnTo=<current-path>`)
- If loading, show a spinner
- If true, render the component

**Signature:**
```jsx
<ProtectedRoute component={Component} />
// or
<ProtectedRoute>
  <TodoApp />
</ProtectedRoute>
```

### `TodoApp.jsx`

**Purpose:**
- Refactored version of the current `App.jsx`; contains all todo list logic
- Expects to be wrapped in `<ProtectedRoute>`
- Header now includes a logout button

**Structure:**
```jsx
export default function TodoApp() {
  const { user, logout } = useAuth();
  const [todos, setTodos] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // ... (same todo logic from current App.jsx)

  return (
    <main className="app">
      <header>
        <h1>TODO — {user?.name || user?.email}</h1>
        <button onClick={logout}>Logout</button>
      </header>
      {/* ... rest of UI ... */}
    </main>
  );
}
```

### `LoginButton.jsx` & `LogoutButton.jsx`

**LoginButton:**
- Simple button that calls `authContext.login()`
- Shows spinner while redirecting

**LogoutButton:**
- Simple button that calls `authContext.logout()`
- No confirmation needed (CSRF-safe because it's POST with token)

## Routing Structure

```
App.jsx routes:
  /login              → <LoginPage />
  /callback           → <CallbackPage />
  /app                → <ProtectedRoute><TodoApp /></ProtectedRoute>
  /404 (or *)         → <NotFoundPage />

Redirects:
  - Unauthenticated user hits /app → redirect to /login
  - Authenticated user hits /login → redirect to /app (optional UX improvement)
  - Callback with error → stay on /callback, show error + link to /login
```

**Implementation note:** Use `react-router-dom` for routing (add to `package.json` dependencies). The `vite.config.js` already proxies `/api` calls to the backend.

## API Client Changes (`api.js`)

**Current state:**
- Bare fetch wrapper; no auth headers

**Required changes:**

1. **Token injection:**
   ```javascript
   // Every request (except /auth/*) gets:
   headers: {
     "Authorization": `Bearer ${localStorage.getItem("auth:accessToken")}`
   }
   ```

2. **401 retry logic:**
   ```javascript
   async function handleResponse(res) {
     if (res.status === 401) {
       // Try to refresh
       const refreshed = await authContext.refreshToken();
       if (refreshed) {
         // Retry original request with new token
         return retryOriginalRequest(res.request);
       } else {
         // Refresh failed; logout
         authContext.logout();
         throw new Error("Session expired. Please log in again.");
       }
     }
     if (!res.ok) {
       const body = await res.json().catch(() => ({}));
       throw new Error(body.error || `Request failed (${res.status})`);
     }
     return res.status === 204 ? null : res.json();
   }
   ```

3. **Error transparency:**
   - Network errors (timeout, offline) should surface as "Network error" to the caller
   - 401 → trigger refresh-and-retry (hidden from caller)
   - Other errors (400, 403, 500) → pass through to caller

## External Dependencies

**New to add in `frontend/package.json`:**

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.x"  // For routing + navigation
  }
}
```

No additional auth libraries needed; use native `fetch` + localStorage + context API.

## Error Boundaries

| Failure Scenario                  | Component           | Handling                                       |
| --------------------------------- | ------------------- | ---------------------------------------------- |
| Login-url fetch fails (500)       | LoginPage           | Show error; offer retry                        |
| User denies consent on Google     | Google redirects to /callback with `error=access_denied` | CallbackPage shows error; link to login |
| Code expired (user took >10 min)  | CallbackPage        | 400 from backend; show "Link expired, try again" |
| State mismatch (CSRF attempt)     | CallbackPage        | 400 `invalid_state`; show security warning    |
| Access token missing on request   | api.js              | Request fails with 401; trigger refresh       |
| Refresh token expired/revoked     | api.js (refresh)    | 401; clear state, redirect to /login          |
| Network timeout                   | api.js              | Catch + throw "Network error"; no retry       |
| Browser localStorage unavailable  | AuthContext         | Fallback to session-only (no persistence)     |

## Key Design Decisions

1. **Token split:**
   - Access token in `localStorage` (readable, short-lived, ok for XSS) because it's needed for every request
   - Refresh token in httpOnly cookie (secure, not readable, CSRF-protected by SameSite) — backend sets/clears it
   - This avoids the "token in localStorage is XSS-vulnerable" gotcha while keeping the refresh token truly secure

2. **State in sessionStorage:**
   - CSRF token (`state`) stored in `sessionStorage` (not persistent across tabs, but sufficient for single-page flow)
   - Validated on callback to prevent CSRF attacks

3. **AuthContext location:**
   - Wraps the entire app in `main.jsx` so all routes and components can call `useAuth()`
   - Manages login/logout state centrally; no prop drilling

4. **ProtectedRoute pattern:**
   - Wraps components (not routes) for maximum flexibility; component can be passed as a prop or children
   - Checks `isLoading` and `isAuthenticated` to decide what to render

5. **No token refresh on every request:**
   - Only refresh on 401; avoids unnecessary server calls
   - Backend's token expiry (15 min) gives a comfortable window

6. **Graceful degradation:**
   - If localStorage is unavailable (private browsing in Safari, user disabled it), app still works in-session
   - Tokens are not persisted across page refreshes in that case (user must re-login)

## Suggested Implementation Order

1. **Add `react-router-dom` to dependencies** and update `package.json`.
2. **Create `context/AuthContext.jsx`** — state management + login/logout/refresh logic.
3. **Create `pages/LoginPage.jsx`, `pages/CallbackPage.jsx`, `pages/NotFoundPage.jsx`**.
4. **Create `components/ProtectedRoute.jsx`, `components/LoginButton.jsx`, `components/LogoutButton.jsx`**.
5. **Refactor current `App.jsx` → `components/TodoApp.jsx`**; add logout button to header.
6. **Update `main.jsx`** — wrap app in `<AuthProvider>`.
7. **Create new `App.jsx`** — conditional routing (login | callback | protected /app).
8. **Update `api.js`** — Bearer token injection, 401 → refresh → retry, error handling.
9. **Update `styles.css`** — add loading spinners, error messages, login page styles.
10. **Test with the backend** — ensure callback flow works end-to-end, tokens refresh, logout clears state.

## Open Questions

1. Should accessing `/app` while unauthenticated redirect to `/login`, or show an access-denied page?
2. Should the app persist a `?returnTo=` param so users return to the original page after login?
3. Should there be a "forgot password" or account recovery flow? (Out of scope for OAuth2/OIDC.)
4. Should the app show a warning if the access token is about to expire (e.g., 1 min before 15-min expiry)?
5. Should logout be a soft logout (clear local state) or hard logout (call backend endpoint)? Design specifies POST `/api/auth/logout` — implement as hard logout.
