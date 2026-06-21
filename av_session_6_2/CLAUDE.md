# CLAUDE.md — HealthTrack

Guidance for Claude when working in `av_session_6_2/`. This is a self-contained
demo app (it is **not** the multi-agent TODO lab described by the repo-root
CLAUDE.md). Treat this directory as its own project.

## What this is

**HealthTrack** — a personal health-metrics tracking app. A Python/Flask API
(Postgres + Redis) plus a React + Vite frontend served by nginx, orchestrated
with Docker Compose. It was built from a slide deck specifying a production
deployment stack (multi-stage Dockerfile, non-root, healthchecks, compose with
api + postgres + redis, `.env`/`.env.example`/`.dockerignore`, dependency-aware
`/health`).

## Services (docker-compose.yml)

| Service  | Image / build                     | Port (cont.) | Published | Health probe              |
| -------- | --------------------------------- | ------------ | --------- | ------------------------- |
| frontend | `./frontend` (node → nginx)       | 3000         | 3000      | `wget /healthz`           |
| api      | `.` (python:3.11-slim multi-stage)| 8000         | 8000      | `curl /health`            |
| db       | `postgres:15-alpine`              | 5432         | internal  | `pg_isready -U $DB_USER`  |
| cache    | `redis:7-alpine`                  | 6379         | internal  | (none, per spec)          |

Startup ordering via `depends_on: { condition: service_healthy }`:
`db → api → frontend`.

## Architecture & conventions

### Backend (`app/`, Flask, ESM-free Python)
- **Layering:** `routes.py` (HTTP) → `extensions.py` (db/cache singletons) →
  `models.py` (SQLAlchemy). Keep HTTP concerns in routes; persistence in models.
- **App discovery:** `app/__init__.py` exposes a module-level `app =
  create_app()` so `flask run` (with `FLASK_APP=app`, set in the Dockerfile)
  finds it. Tables are created via `db.create_all()` inside the factory.
- `db = SQLAlchemy()`; `cache = redis.from_url(REDIS_URL)` (lazy — safe to
  construct before Redis is up).
- **`/health`** pings DB (`SELECT 1`) and Redis (`ping()`); each check is `"ok"`
  or the error string; returns **200** only if all checks pass, else **503**.
  Keep this contract — the Docker healthcheck and load-balancer behavior depend on it.
- Routes live on a Blueprint `bp` (`api`). Errors return JSON `{"error": ...}`
  with appropriate status (400 invalid, 404 not found).

### Frontend (`frontend/`, React 18 + Vite)
- Single component `src/App.jsx`. Calls the API at **`/api/...`** (relative).
- In Docker, **nginx proxies `/api/*` → `api:8000`** (`frontend/nginx.conf`), so
  there is **no CORS** setup. For local `npm run dev`, `vite.config.js` proxies
  `/api` → `localhost:8000`.
- nginx listens on **3000** and runs **non-root** (`nginxinc/nginx-unprivileged`).

### Docker
- Both app images are **multi-stage**: a builder stage, then a slim/non-root
  runtime that copies only built artifacts.
- API runtime installs `curl` (needed by its healthcheck; slim base lacks it).
- Root `.dockerignore` excludes `.env`, `.git`, `__pycache__`, and `frontend/`
  from the API build context. `frontend/.dockerignore` excludes `node_modules/`,
  `dist/`.
- **No secrets in code** — config is via env vars / `.env` (gitignored). `.env.example`
  is the committed template.

## Running & testing

```bash
./startup.sh          # build, start all, wait for healthy, print URLs
./startup.sh down     # docker compose down -v (clean slate)
```

Manual: `docker compose build && docker compose up -d && docker compose ps`.
The app: UI at http://localhost:3000, API at http://localhost:8000.

End-to-end smoke test (also exercises the proxy and the degraded path):

```bash
curl -X POST localhost:8000/metrics -H 'Content-Type: application/json' \
  -d '{"type":"steps","value":8421,"unit":"count"}'      # 201
curl localhost:8000/metrics                                # source: database, then cache
curl localhost:3000/api/health                             # proxied -> 200
docker compose stop cache && curl -i localhost:8000/health # -> 503; then `start cache`
```

## Gotchas (learned the hard way)

- **Port 5000 is unusable on this host** — macOS Control Center / AirPlay holds
  it. The whole app uses **8000** for the API instead. Don't reintroduce 5000.
- **Container healthchecks must use `127.0.0.1`, not `localhost`** — busybox
  `wget` (frontend) tries IPv6 `::1` first and the servers listen on IPv4 only.
- **Compose merges `ports:` by concatenation**, not replacement. To override a
  port mapping in an extra `-f` file, use the `!override` YAML tag.
- `flask run` prints a "development server" WARNING — expected, not an error.

## Spec deviations (vs. the original images)

- Port **8000** instead of 5000 (by request).
- `curl` added to the API runtime image; `ENV FLASK_APP=app` added.
- `db.session.execute(text('SELECT 1'))` instead of `db.execute(...)`; routes on
  a Blueprint instead of `@app.route`.
- The **frontend** service is an addition beyond the original API-only spec.

When changing ports, healthchecks, or the `/health` contract, update **all** of:
the relevant Dockerfile, `docker-compose.yml`, `startup.sh`, and this file.
