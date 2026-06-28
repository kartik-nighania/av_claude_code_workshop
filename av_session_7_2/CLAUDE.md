# CLAUDE.md — OrderTrack API

Guidance for Claude (and humans) working in `av_session_7_2/`. Read this before
making changes.

## 1. Project overview & tech stack

**OrderTrack** is a small order-tracking demo: a Flask REST API backed by
PostgreSQL (system of record) and Redis (read-through cache for order status),
with a React + Vite single-page frontend.

- **Backend:** Python 3.12, Flask + Flask-SQLAlchemy, Flask-CORS, `redis-py`,
  `psycopg2-binary`. App factory in `app/__init__.py` (`create_app`); WSGI entry
  in `wsgi.py`. Served on **:8010**.
- **Frontend:** React 18 + Vite (`frontend/`), thin `fetch` wrapper in
  `frontend/src/api.js`. Served on **:5173**; Vite proxies `/api/*` → `:8010`.
- **Data stores:** PostgreSQL 15 and Redis 7, run as standalone Docker containers
  (no docker-compose for the app itself).

**Layout**

```
app/
  __init__.py      # create_app(): CORS, blueprints, db.create_all + seed, error handlers
  config.py        # Config from env vars (DATABASE_URL, REDIS_URL, SECRET_KEY, TTL)
  extensions.py    # db (SQLAlchemy) + Redis client holder
  models.py        # Customer, Product, Order, OrderItem; ORDER_STATUSES
  order_status.py  # cache-aside read + invalidation for order status
  seed.py          # idempotent demo data
  routes/          # blueprints: health, customers, products, orders
frontend/          # React + Vite SPA
wsgi.py            # dev entry (app.run, debug=True, :8010)
startup.sh         # boots Postgres + Redis containers, backend, frontend
```

## 2. How to run locally

```bash
./startup.sh          # starts Postgres + Redis containers, backend (:8010), frontend (:5173)
```

Then open http://localhost:5173.

Manual / piecemeal:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python wsgi.py                       # backend only, :8010

cd frontend && npm install && npm run dev   # frontend only, :5173
```

Config comes from env vars (see `app/config.py`); copy `.env.example` → `.env` to
override `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ORDER_STATUS_CACHE_TTL`.
Schema is created at boot via `db.create_all()` and seeded by `seed_data()`.

## 3. Coding conventions

- **Layering:** `routes (blueprints) → models (SQLAlchemy) → Postgres`, with Redis
  as a side cache. HTTP concerns (parse JSON, status codes, validation) live in the
  route handlers; **there is no service layer yet** — keep new logic consistent with
  this until a service layer is introduced (see §6).
- Each resource is a **blueprint** under `app/routes/` with `url_prefix="/api/..."`,
  using `@bp.get/post/put/delete`. Use `Model.query.get_or_404(id)` for single-item
  reads.
- Models expose a **`to_dict()`** for serialization; responses go through `jsonify`.
  `unit_price` is snapshotted onto `OrderItem` at order time; `Order.total` is a
  computed Python property, not a stored column.
- **Validation** is inline and minimal (`if not data.get("field")` → `400`). Order
  status is validated against `ORDER_STATUSES`.
- **Redis access is null-safe** — every call guards `if cache is not None` and
  degrades to DB-only. Preserve this.
- **Config from env vars only** (`os.environ.get`); no secrets hard-coded beyond the
  documented dev defaults.
- **Style:** PEP 8, 4-space indent, module + function docstrings, snake_case.
  Frontend: ES modules, 2-space indent, the existing `api.js` request-wrapper shape.
- Match the surrounding file's style; keep comments purposeful, not decorative.

## 4. What Claude is allowed to generate

Without prior sign-off, Claude may:

- Add/modify **route handlers, models, serialization, and cache logic** following the
  existing layering and conventions.
- Add **new blueprints/endpoints** consistent with the `/api/...` pattern.
- Write **tests** (`pytest`), `docs/`, and developer tooling/config.
- Frontend: components, API-wrapper methods, and UI wiring in `frontend/src/`.
- Refactors that are **behavior-preserving** and localized.
- Bug fixes and validation hardening that don't change public API shapes.

## 5. What requires human review

Flag and get explicit human approval before:

- **Auth / authorization** changes, or anything touching `SECRET_KEY`, secrets, or
  credential handling.
- **CORS, `debug` mode, or other security-affecting config** (`config.py`, `wsgi.py`).
- **Schema / data-model changes** — there are **no migrations** (Alembic), so model
  edits affect `db.create_all()` behavior and can require a manual DB reset.
- **Breaking API changes**: removing/renaming endpoints or fields, changing status
  codes or response shapes the frontend depends on (`frontend/src/api.js`).
- Anything altering **order status transition rules**, pricing/`total`, or stock.
- Adding **new dependencies**, changing `startup.sh`, ports, or deployment topology.
- Deleting data, dropping tables, or destructive migrations/seed changes.

## 6. Known limitations

This is a **starter scaffold** — basic CRUD only. Notable gaps (do not assume these
exist):

- **No authentication/authorization** on any endpoint; all routes are open.
- **No service layer** — business logic lives in route handlers.
- **No migrations** — schema via `db.create_all()` at boot; `seed_data()` runs every
  startup.
- **No tests** currently (`requirements.txt` has no pytest).
- **Wide-open CORS** (`CORS(app)`), `SECRET_KEY` defaults to `"dev-secret-key"`,
  `debug=True` in `wsgi.py` — all dev-only, unsafe for production.
- **No stock enforcement** (orders can exceed `stock`; stock is never decremented),
  **no order status state machine** (any status → any status), **no pagination/
  filtering** on list endpoints.
- Deleting a customer/product still referenced by an order can raise a FK error.
- App is not containerized; runs on the host via the Flask dev server (no gunicorn).

See `docs/ARCHITECTURE.md` for the full architecture, endpoint inventory, and a
phased plan to close these gaps.

## 7. How to run tests

**There is currently no test suite.** When adding tests, use **pytest** (with
`pytest-flask`/Supertest-style integration), place them under `tests/`, and add the
dev deps to `requirements.txt` (or a `requirements-dev.txt`). Target:

```bash
pip install pytest pytest-flask
pytest                 # once tests exist under tests/
```

Cover at minimum: each endpoint's happy path, `400`/`404`/validation cases, and the
Redis cache hit/miss/invalidate behavior in `app/order_status.py`. A Postgres + Redis
instance (or test doubles) must be reachable for integration tests.
