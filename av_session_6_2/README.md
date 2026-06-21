# HealthTrack

A small **personal health-metrics tracking app**, used as a demo for a
production-style deployment stack. It pairs a Python/Flask API with a React + Vite
frontend and runs as a four-service Docker Compose project:

- **Multi-stage Docker builds** (builder + slim/non-root runtime) for both app images
- **Postgres** for storage, **Redis** for caching
- A **dependency-aware `/health`** endpoint (returns `503` when a dependency is down)
- **Health checks + `depends_on` ordering** so nothing starts before its deps are ready

> **Quick start:** `./startup.sh`, then open **http://localhost:3000**.

---

## Use case

Log and retrieve personal health readings — steps, weight, heart rate, sleep
hours, etc. Readings persist in Postgres; the list endpoint is cached in Redis
(with cache invalidation on write). The React UI shows live API/dependency
health, a form to log metrics, and a table of recorded readings.

---

## Architecture

```
                  ┌─────────────────────────────────────────────┐
  Browser  ──▶    │  frontend (nginx, :3000)                     │
  :3000           │   • serves the React/Vite static bundle      │
                  │   • proxies /api/* ─▶ api:8000               │
                  └───────────────┬─────────────────────────────┘
                                  │  /api/* (no CORS)
                  ┌───────────────▼─────────────────────────────┐
  curl     ──▶    │  api (Flask, :8000)                          │
  :8000           │   • /health pings db + cache                 │
                  │   • /metrics CRUD                            │
                  └─────────┬───────────────────┬───────────────┘
                            │                   │
                  ┌─────────▼────────┐  ┌───────▼──────────┐
                  │ db  postgres:15  │  │ cache  redis:7    │
                  │ (postgres_data)  │  │ (redis_data)      │
                  └──────────────────┘  └───────────────────┘
```

Startup ordering: `db` becomes healthy → `api` starts and becomes healthy →
`frontend` starts (`depends_on: condition: service_healthy` at each step).

---

## Project structure

```
av_session_6_2/
├── app/                     # Flask API (package; FLASK_APP=app)
│   ├── __init__.py          #   create_app() factory + module-level `app`
│   ├── extensions.py        #   db = SQLAlchemy(), cache = redis.from_url(...)
│   ├── models.py            #   Metric model
│   └── routes.py            #   /, /health, /metrics CRUD (Blueprint)
├── frontend/                # React + Vite UI, served by non-root nginx
│   ├── src/{main.jsx,App.jsx,styles.css}
│   ├── index.html
│   ├── vite.config.js       #   dev proxy /api -> localhost:8000
│   ├── nginx.conf           #   listen 3000; proxy /api/ -> api:8000; SPA fallback
│   ├── Dockerfile           #   node build -> nginx-unprivileged runtime
│   └── .dockerignore
├── Dockerfile               # API image: python:3.11-slim builder + runtime, non-root
├── docker-compose.yml       # frontend + api + db + cache, healthchecks, volumes
├── requirements.txt
├── .env.example             # committed template (safe placeholders)
├── .env                     # real values (gitignored)
├── .dockerignore            # excludes .env, .git, __pycache__, frontend/, ...
├── startup.sh               # build + up + wait-for-healthy + print URLs
└── README.md
```

---

## API reference

Base URL: `http://localhost:8000` (or via the UI proxy at `http://localhost:3000/api`).

| Method & path        | Description                                          | Codes        |
| -------------------- | ---------------------------------------------------- | ------------ |
| `GET /`              | Service info + endpoint list                         | 200          |
| `GET /health`        | Liveness + dependency check (Postgres + Redis)       | 200 / 503    |
| `POST /metrics`      | Record a metric — JSON `{type, value, unit?}`        | 201 / 400    |
| `GET /metrics`       | List metrics (served from Redis cache when warm)     | 200          |
| `GET /metrics/<id>`  | Fetch a single metric                                | 200 / 404    |

```bash
# Record a metric
curl -X POST http://localhost:8000/metrics \
  -H 'Content-Type: application/json' \
  -d '{"type":"steps","value":8421,"unit":"count"}'

# List (first call -> "source":"database", subsequent -> "source":"cache")
curl http://localhost:8000/metrics

# Health (200 healthy; 503 if a dependency is down)
curl http://localhost:8000/health
```

Health response shape:

```json
{ "status": "ok", "checks": { "database": "ok", "cache": "ok" } }
```

If a dependency is down, its check holds the error string and the HTTP status is `503`.

---

## Configuration

Config comes from environment variables (loaded via `env_file: .env`). Copy the
template and fill in real values — `.env` is gitignored:

```bash
cp .env.example .env
```

| Variable            | Example                  | Used by            |
| ------------------- | ------------------------ | ------------------ |
| `FLASK_ENV`         | `development`            | Flask              |
| `FLASK_DEBUG`       | `1`                      | Flask              |
| `SECRET_KEY`        | `change-me-in-production`| Flask sessions     |
| `DB_HOST`           | `db`                     | API → Postgres     |
| `DB_PORT`           | `5432`                   | API → Postgres     |
| `DB_NAME`           | `healthtrack`            | API + Postgres     |
| `DB_USER`           | `healthtrack_user`       | API + Postgres     |
| `DB_PASSWORD`       | `CHANGE_ME`              | API + Postgres     |
| `ANTHROPIC_API_KEY` | `sk-ant-CHANGE_ME`       | reserved (unused)  |
| `REDIS_URL`         | `redis://cache:6379/0`   | API → Redis        |

---

## Running it

### One command

```bash
./startup.sh          # build, start, wait until healthy, print URLs
./startup.sh down     # stop + remove containers and volumes (clean slate)
```

### The manual runbook

```bash
docker compose build      # 1. build all service images (shows layer caching)
docker compose up -d      # 2. start frontend + api + db + cache
docker compose ps         # 3. status — api/db/frontend should be 'healthy'
curl http://localhost:8000/health   # 4. -> {"status":"ok", ...}
docker compose logs api   # 5. tail logs — look for ERROR / WARNING
docker compose down -v    # 6. stop + remove containers and volumes
```

### Local dev without Docker (optional)

```bash
# API
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs) DB_HOST=localhost REDIS_URL=redis://localhost:6379/0
FLASK_APP=app python -m flask run --host=0.0.0.0 --port=8000

# Frontend (proxies /api -> localhost:8000)
cd frontend && npm install && npm run dev   # http://localhost:5173
```

---

## Health check design

- **Docker health check** — each app container runs an HTTP health probe; an
  unhealthy container is reported by `docker compose ps` and can be pulled by an
  orchestrator.
- **Compose `depends_on`** — `api` waits for `db` to be healthy; `frontend` waits
  for `api` to be healthy. No startup race conditions.
- **503 on degraded** — `/health` returns `503` if Postgres *or* Redis is
  unreachable, so a load balancer drops the instance. Verify:

  ```bash
  docker compose stop cache
  curl -i http://localhost:8000/health      # -> HTTP/1.1 503, checks.cache = error
  docker compose start cache
  curl -i http://localhost:8000/health      # -> HTTP/1.1 200
  ```

---

## Ports

| Service  | Container | Published | URL                     |
| -------- | --------- | --------- | ----------------------- |
| frontend | 3000      | 3000      | http://localhost:3000   |
| api      | 8000      | 8000      | http://localhost:8000   |
| db       | 5432      | (internal)| —                       |
| cache    | 6379      | (internal)| —                       |

The API listens on `8000` **everywhere** (container, Dockerfile
`EXPOSE`/`HEALTHCHECK`/`CMD`, and the `8000:8000` mapping). Port `5000` is
intentionally avoided because macOS Control Center / AirPlay Receiver holds it on
this host.

---

## Notes on the spec

This app was built from a slide deck specifying a "HealthTrack API (Flask)"
deployment stack. It follows that spec closely. Intentional differences:

- **Port 8000 instead of 5000** — by request, to dodge the macOS AirPlay conflict.
- **`curl` installed in the API runtime image** — the slim base ships without it,
  but the healthcheck needs it.
- **`flask run`** (dev server) is used as the CMD, matching the spec — not a
  production WSGI server like gunicorn.
- The **frontend** service is an addition beyond the original (API-only) spec.
