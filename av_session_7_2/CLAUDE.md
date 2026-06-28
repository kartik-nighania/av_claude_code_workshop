# CLAUDE.md — OrderTrack API

Guidance for Claude (and humans) working in **this** directory (`av_session_7_2`).
This is a self-contained capstone repo — do not wander into sibling `av_session_*`
folders.

## 1. Project overview & tech stack

OrderTrack is a small **order-tracking REST API**: a Flask backend backed by
PostgreSQL (system of record) and Redis (read cache for order status), with a
React/Vite frontend.

- **Backend:** Python 3.12, Flask 3 + Flask-SQLAlchemy 2 (SQLAlchemy 2.0),
  Flask-Cors, `psycopg2-binary`, `redis`. Served on `:8010`.
- **Frontend:** React 18 + Vite 5 (ESM), served on `:5173`, proxies `/api/*` to `:8010`.
- **Data stores:** PostgreSQL 15 + Redis 7, run as plain `docker run` containers
  (`ordertrack-postgres`, `ordertrack-redis`). No docker-compose.
- **Layering:** `routes (blueprints) → models (SQLAlchemy ORM) → Postgres`, with
  Redis as a cache-aside layer for `/api/orders/<id>/status` (`order_status.py`).

Key files: `app/__init__.py` (app factory), `app/models.py` (Customer, Product,
Order, OrderItem), `app/routes/*` (blueprints), `app/order_status.py` (cache),
`app/config.py`, `app/extensions.py` (db + redis), `wsgi.py`, `app/seed.py`.

## 2. How to run locally

Requires Docker running (for Postgres + Redis).

```bash
./startup.sh
```

This: starts/creates the Postgres + Redis containers, creates `.venv`, installs
`requirements.txt`, runs the Flask backend on `:8010`, and the Vite frontend on
`:5173`. Open http://localhost:5173. Ctrl-C stops backend + frontend (DB
containers keep running).

Backend only (containers must already be up, env vars set):
```bash
source .venv/bin/activate
python wsgi.py            # http://localhost:8010/api/health
```

Config comes from env vars with dev defaults: `DATABASE_URL`, `REDIS_URL`,
`SECRET_KEY`, `ORDER_STATUS_CACHE_TTL`, `PORT`. Copy `.env` to override.

## 3. Coding conventions used

- **Backend layering is strict:** HTTP concerns (request parsing, status codes,
  `jsonify`) live in `app/routes/*`; persistence/models live in `app/models.py`.
  Keep new business logic out of route bodies where practical.
- **Blueprints** per resource, each with a `url_prefix` (`/api/orders`, etc.).
  Use the `@bp.get/.post/.put/.delete` shorthand decorators (Flask 3 style).
- **Validation today is inline & minimal:** presence checks returning
  `jsonify(error=...), 400`; `get_or_404` for missing rows. Match this style.
- **Models** expose a `to_dict()` for serialization; statuses are constrained to
  `ORDER_STATUSES` (`pending, paid, shipped, delivered, cancelled`).
- **Cache discipline:** read order status only via `get_order_status`; always
  call `invalidate_order_status(id)` after a status change or delete.
- **Errors:** return JSON `{"error": "..."}` with an appropriate status; the app
  has global 400/404 handlers.
- **Frontend:** ESM, functional React, all API calls go through the `api` object
  in `frontend/src/api.js` (thin `fetch` wrapper) — don't call `fetch` directly
  in components.
- **No secrets in code.** Config via env vars only.

## 4. What Claude is allowed to generate

- New/edited route handlers, models, services, and the Redis cache layer,
  following the layering above.
- Input validation, error handling, pagination/filtering on list endpoints.
- A service layer (`app/services/`) to move business rules out of routes.
- Tests under `tests/` (pytest + Flask test client) and fixtures.
- Frontend components and additions to `frontend/src/api.js`.
- Infra/config scaffolding: `docker-compose.yml`, `Dockerfile`, Alembic
  migrations, CI/CD workflow files, `.env.example`.
- Docs in `docs/` (e.g. `docs/ARCHITECTURE.md`).

## 5. What requires human review

- **Anything security-sensitive:** auth/JWT, password hashing, CORS origin
  policy, `SECRET_KEY` handling, rate limiting. Propose, don't silently ship.
- **Schema/data changes:** model migrations, dropping columns, changes to
  `seed.py` or `db.create_all()` boot behavior.
- **Money/stock logic:** order totals, `unit_price` snapshotting, stock
  decrement, status-transition rules — get sign-off before changing.
- **Anything touching `.env` / real credentials or deployment targets (EC2).**
- **Dependency additions/upgrades** in `requirements.txt` / `package.json`.
- Do not edit files outside this repo, including sibling `av_session_*` folders.

## 6. Known limitations of this codebase

- **No authentication/authorization** — every endpoint is public; `CORS(app)`
  allows all origins; `SECRET_KEY` defaults to `dev-secret-key`.
- **No business rules:** order creation does not check or decrement stock; any
  status → any status is allowed (no transition state machine).
- **No migrations:** `db.create_all()` + `seed_data()` run on every boot.
- **Uniqueness conflicts** (duplicate email/SKU) surface as 500s, not 409s.
- **No pagination/filtering/sorting** on list endpoints.
- **Dev server only** (`python wsgi.py`) — no Gunicorn/uWSGI; no docker-compose;
  no CI/CD; minimal logging/metrics/tracing.
- **Tests are not currently present in source** — only compiled `.pyc` files
  remain under `tests/__pycache__/` (test_auth, test_orders, test_products,
  test_customers, conftest). The test sources need to be regenerated.

## 7. How to run tests

`pytest` (with coverage, flake8, black, bandit, safety) is installed in `.venv`.

```bash
source .venv/bin/activate
pytest                       # run the suite
pytest -q tests/test_orders.py
pytest --cov=app             # with coverage
```

> ⚠️ Test source files are currently missing (only `.pyc` artifacts remain).
> Recreate them under `tests/` with a `conftest.py` that builds the app via
> `create_app` with a test config and a Flask test client before `pytest` will
> collect anything. Lint/security checks: `flake8 app`, `black app`,
> `bandit -r app`, `safety check`.
