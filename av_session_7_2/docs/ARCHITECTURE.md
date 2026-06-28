# OrderTrack — Architecture

A small order-tracking demo: a **Flask REST API** backed by **PostgreSQL** (system
of record) and **Redis** (read-through cache for order-status lookups), with a
**React + Vite** single-page frontend.

> **Status:** starter scaffold — basic CRUD only, no auth, no tests, no migrations.
> This document is the shared contract for the capstone build-out (see §5).

---

## 1. System architecture diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                   Browser                                       │
│                                                                                 │
│   React SPA (Vite dev server, :5173)                                            │
│   frontend/src/App.jsx ── tabs: orders | products | customers | new order       │
│        │                                                                        │
│        │  fetch("/api/...")   frontend/src/api.js  (thin fetch wrapper)         │
│        ▼                                                                         │
│   Vite dev proxy  ──  /api/* ──►  http://localhost:8010   (vite.config.js)      │
└────────┼────────────────────────────────────────────────────────────────────────┘
         │  HTTP (JSON)
         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  Flask app  (wsgi.py → app/create_app)              :8010                       │
│                                                                                 │
│   CORS(app)  ──►  error handlers (404 / 400 → JSON)                             │
│                                                                                 │
│   Blueprints (app/routes/)                                                      │
│   ┌─────────────┬──────────────┬───────────────┬───────────────────────────┐  │
│   │ health_bp   │ customers_bp │ products_bp   │ orders_bp                  │  │
│   │ /api/health │ /api/customers│ /api/products│ /api/orders                │  │
│   └─────┬───────┴──────┬───────┴───────┬───────┴───────┬────────────────────┘  │
│         │              │               │               │                        │
│         │              ▼               ▼               ▼                        │
│         │        SQLAlchemy models (app/models.py)                             │
│         │        Customer · Product · Order · OrderItem                        │
│         │              │                       │                                │
│         │              │                       │  order status read path        │
│         │              │                       ▼                                │
│         │              │      app/order_status.py  get_order_status()           │
│         │              │              │            invalidate_order_status()     │
│         │              │              │ (1) check Redis  (2) fall back to DB     │
│         ▼              ▼              ▼                                          │
│   ┌──────────────────────────┐   ┌──────────────────────────┐                  │
│   │  db (SQLAlchemy session)  │   │  Redis client            │                  │
│   │  app/extensions.py: db    │   │  app/extensions.py:       │                  │
│   └────────────┬─────────────┘   │  get_redis()             │                  │
│                │                  └────────────┬─────────────┘                  │
└────────────────┼────────────────────────────────┼──────────────────────────────┘
                 │ psycopg2                        │ redis-py
                 ▼                                 ▼
        ┌──────────────────┐              ┌──────────────────┐
        │ PostgreSQL 15    │              │ Redis 7          │
        │ (docker) :5432   │              │ (docker) :6379   │
        │ ordertrack DB    │              │ key: order_status:<id>
        │ customers/products│              │ TTL = 30s        │
        │ orders/order_items│              └──────────────────┘
        └──────────────────┘
```

**Process / deployment topology (local, via `startup.sh`):**

```
startup.sh
  ├─ docker run postgres:15-alpine  → ordertrack-postgres  (:5432)
  ├─ docker run redis:7-alpine      → ordertrack-redis     (:6379)
  ├─ python wsgi.py                 → Flask dev server      (:8010)   [debug=True]
  └─ npm run dev (frontend/)        → Vite dev server       (:5173)
```

There is **no docker-compose and no container for the app itself** — the two data
stores run as standalone `docker run` containers; the Flask and Vite processes run
on the host. Schema is created at boot via `db.create_all()` and `seed_data()`
(idempotent) inside `create_app()`.

---

## 2. Data flow: request → service → DB

### 2.1 Layering

The backend is intentionally thin — there is **no dedicated service layer**;
blueprints call the SQLAlchemy models directly. The one piece of genuine business
logic that lives outside a route is the cached status read in
`app/order_status.py`.

```
HTTP request
   → Blueprint route handler (app/routes/*.py)      ── parse JSON, validate, status codes
       → SQLAlchemy model / query (app/models.py)   ── ORM objects, .to_dict()
           → db.session  (Postgres via psycopg2)    ── persistence
       → (orders only) order_status.py              ── Redis read-through + invalidation
   ← jsonify(...) response
```

### 2.2 Write path — e.g. `POST /api/orders`

```
1. orders.create_order()             request.get_json(silent=True)
2. validate                          customer_id + at least one item required → 400 if missing
3. build Order(status="pending")
4. for each item:  Product.query.get(product_id)        # 400 if product missing
                   append OrderItem(unit_price = product.price)   # price snapshotted from product
5. db.session.add(order); db.session.commit()           # INSERT orders + order_items
6. return order.to_dict(), 201                           # total computed in-Python from items
```

Note: `Order.total` is a **computed Python property** (`Σ quantity × unit_price`),
not a stored column — it is recalculated on every serialization.

### 2.3 Read path with cache — `GET /api/orders/<id>/status`

```
get_order_status(order_id):
  cache_key = "order_status:<id>"
  ┌─ Redis GET cache_key
  │     hit  → JSON-decode, add source="cache", RETURN          (fast path)
  │     miss ↓
  ├─ Order.query.get(order_id)
  │     None → RETURN None  → route responds 404
  ├─ payload = {order_id, status, total}
  ├─ Redis SETEX cache_key  TTL=ORDER_STATUS_CACHE_TTL(30s)  JSON(payload)
  └─ add source="db", RETURN
```

**Invalidation:** `PUT /api/orders/<id>` and `DELETE /api/orders/<id>` call
`invalidate_order_status(id)` after commit (Redis `DEL`), so the next status read
re-populates from Postgres. All Redis calls are **null-safe** — if the client is
unset they silently degrade to DB-only.

### 2.4 Health probe — `GET /api/health`

`SELECT 1` against Postgres + `PING` against Redis; any failure flips the body to
`degraded` and the status code to `503`.

---

## 3. Endpoint inventory

All routes are JSON in / JSON out and live under `/api`. **No authentication on any
endpoint.**

| # | Method | Path | Handler (`app/routes/…`) | Purpose |
|---|--------|------|--------------------------|---------|
| 1 | GET | `/api/health` | `health.py:health` | Liveness of DB + Redis (200 / 503) |
| 2 | GET | `/api/customers` | `customers.py:list_customers` | List customers |
| 3 | GET | `/api/customers/<int:id>` | `customers.py:get_customer` | Get one (404 if missing) |
| 4 | POST | `/api/customers` | `customers.py:create_customer` | Create (`name`, `email` required) |
| 5 | PUT | `/api/customers/<int:id>` | `customers.py:update_customer` | Update name/email |
| 6 | DELETE | `/api/customers/<int:id>` | `customers.py:delete_customer` | Delete |
| 7 | GET | `/api/products` | `products.py:list_products` | List products |
| 8 | GET | `/api/products/<int:id>` | `products.py:get_product` | Get one |
| 9 | POST | `/api/products` | `products.py:create_product` | Create (`name`, `sku` required) |
| 10 | PUT | `/api/products/<int:id>` | `products.py:update_product` | Update fields |
| 11 | DELETE | `/api/products/<int:id>` | `products.py:delete_product` | Delete |
| 12 | GET | `/api/orders` | `orders.py:list_orders` | List orders (with items + total) |
| 13 | GET | `/api/orders/<int:id>` | `orders.py:get_order` | Get one order |
| 14 | GET | `/api/orders/<int:id>/status` | `orders.py:order_status` | **Cached** status lookup |
| 15 | POST | `/api/orders` | `orders.py:create_order` | Create order + items |
| 16 | PUT | `/api/orders/<int:id>` | `orders.py:update_order` | Update status (validated enum) + cache invalidate |
| 17 | DELETE | `/api/orders/<int:id>` | `orders.py:delete_order` | Delete + cache invalidate |

**Data model (Postgres):**

```
customers (id, name, email[unique], created_at)
products  (id, name, sku[unique], price NUMERIC(10,2), stock)
orders    (id, customer_id→customers, status, created_at)
order_items (id, order_id→orders[cascade delete], product_id→products, quantity, unit_price)

Order.total  = Σ(order_items.quantity × order_items.unit_price)   # computed, not stored
ORDER_STATUSES = pending → paid → shipped → delivered → cancelled  # flat set, no transition rules
```

Frontend consumes #1, #2, #7, #12, #15, #16 (`frontend/src/api.js`). #14
(`orderStatus`) is wired in the client but not yet surfaced in the UI.

---

## 4. Missing features vs. production

Grouped by concern; severity reflects production risk. This is the gap list the
capstone closes.

### 4.1 Security & auth — *critical*
- **No authentication or authorization** on any endpoint — every CRUD route is open.
- **No input validation depth**: email format, SKU format, price ≥ 0, quantity ≥ 1,
  stock not enforced (an order can exceed available `stock`; stock is never decremented).
- **`SECRET_KEY` defaults to `"dev-secret-key"`** in `config.py` — usable but unsafe if shipped.
- **CORS is wide open** (`CORS(app)` with no origin allowlist).
- **`debug=True`** in `wsgi.py` — exposes the Werkzeug debugger/PIN; must be off in prod.
- **No rate limiting**, no security headers, no request size limits.
- **No mass-assignment guard** on `PUT` (only `orders` validates the status enum;
  customers/products blindly accept supplied fields).

### 4.2 Data integrity & business rules — *high*
- **No DB migrations** — schema is `db.create_all()` at boot; any model change needs a
  manual drop or an out-of-band migration. No Alembic.
- **No order status transition rules** — any status can jump to any other (e.g.
  `delivered → pending`); `ORDER_STATUSES` is a flat set.
- **No stock management / overselling protection**; `stock` is decorative.
- **`unit_price` snapshot is good**, but there is no currency, tax, discount, or totals column.
- **No pagination / filtering / sorting** on list endpoints — `GET /api/orders` returns all rows.
- **Cascade is partial**: deleting a customer with orders, or a product referenced by
  an order item, will raise a FK error (no cascade / guard on those paths).

### 4.3 Reliability & operations — *high*
- **No app container / docker-compose** — data stores are `docker run`, app runs on host.
- **No production WSGI server** (gunicorn/uvicorn) — uses Flask's dev server.
- **No connection pooling config, retries, or graceful degradation** beyond null-safe Redis.
- **No structured logging, metrics, tracing, or error reporting.**
- **No `/api/health` readiness vs liveness split**, no startup/shutdown hooks.
- **`seed_data()` runs on every boot** inside `create_app()` — fine for demo, wrong for prod.

### 4.4 Quality & delivery — *medium*
- **No tests** (no unit, integration, or e2e) — `requirements.txt` has no pytest.
- **No CI/CD** beyond what lives at the repo root; no lint/format gate, no pre-commit.
- **No API documentation** (OpenAPI/Swagger) or versioning (`/api/v1`).
- **No `.env` loading** (`python-dotenv`) — env vars must be exported manually; `startup.sh` does it.
- **Frontend:** no create/edit forms for products or customers, no error boundary,
  no loading states, no build/deploy pipeline; status-cache endpoint unused in UI.

---

## 5. Proposed capstone implementation plan

Phased so each step is independently shippable and testable. Earlier phases unblock
later ones (auth before deploy; tests alongside everything).

### Phase 0 — Foundation & safety net *(do first)*
1. **Introduce a service layer** between routes and models (`app/services/`), moving
   validation and business rules out of blueprints — matches the repo's intended
   `routes → services → store` discipline and gives tests a seam.
2. **Add a test suite** (`pytest` + `pytest-flask`): unit tests for services, integration
   tests for each endpoint (happy path + 400/404/validation), a Redis cache hit/miss/
   invalidate test. Add `tests/` and a `docs/test_plan.md`.
3. **Add Alembic migrations**; stop calling `db.create_all()`/`seed_data()` at boot in
   non-dev. Seed becomes an explicit CLI command.
4. **Tooling gate:** `ruff`/`black` + `pre-commit`, and wire `requirements-dev.txt`.

### Phase 1 — Correctness & domain rules
5. **Validation everywhere:** email/SKU format, `price ≥ 0`, `quantity ≥ 1`; reject
   unknown/extra fields on writes (guard mass-assignment).
6. **Order status state machine:** allow only legal transitions; reject illegal jumps with 400.
7. **Stock enforcement:** decrement `product.stock` on order creation in a transaction;
   reject orders that exceed stock; restore on cancel.
8. **List ergonomics:** pagination, sorting, and basic filtering on the three list endpoints.
9. **Delete safety:** define cascade/guard behavior for customer- and product-deletes.

### Phase 2 — Security & auth
10. **AuthN/AuthZ:** add user accounts + token auth (JWT or session); protect all
    mutating routes; scope orders to their customer where relevant.
11. **Harden config:** require `SECRET_KEY` from env (fail fast if default in prod),
    restrict CORS to known origins, disable `debug`, add security headers + a request-size
    limit, and add rate limiting.
12. **Secrets via env / `.env`** loaded with `python-dotenv`; document required vars.

### Phase 3 — Observability & API surface
13. **Structured logging** + request IDs; central error handler returning consistent JSON.
14. **OpenAPI/Swagger** spec + `/api/v1` versioning; regenerate the README endpoint table from it.
15. **Metrics + readiness/liveness** split on health; optional tracing.

### Phase 4 — Packaging & deployment
16. **Dockerize the app**; add **docker-compose** for app + Postgres + Redis (one `up`).
17. **Production WSGI** (gunicorn) behind the container; configure pool size, workers, timeouts.
18. **CI/CD pipeline:** run lint + tests on PR, build image, deploy (e.g. EC2/container host).

### Phase 5 — Frontend completion
19. Create/edit forms for products & customers; surface the **cached order-status** endpoint.
20. Loading/error states, an error boundary, and a production build + static-hosting step.

---

### Multi-agent execution map (how this repo's agent team builds §5)

| Phase | Lead agent | Output artifact |
|-------|-----------|-----------------|
| 0–1 design | Architect | this doc, kept current |
| 0 tests | Test agent | `tests/`, `docs/test_plan.md` |
| 2 security | Security agent | `docs/security_findings.json` |
| all | Reviewer | `docs/review.md` |
| merge | Orchestrator | `docs/action_plan.md` (prioritized) |

Recommended first slice end-to-end: **Phase 0 (service layer + tests + migrations)**,
since it de-risks every later change and establishes the validation seam the security
and domain-rule work depends on.
