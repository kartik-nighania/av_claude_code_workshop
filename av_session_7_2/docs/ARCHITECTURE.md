# OrderTrack API — Architecture

A small order-tracking service: Flask REST API backed by PostgreSQL (system of
record) and Redis (read cache for order status), with a React/Vite frontend.

- **Backend:** Flask 3 + Flask-SQLAlchemy 2 (ESM-style blueprints), served on `:8010`
- **Frontend:** React + Vite, served on `:5173`
- **Data:** PostgreSQL 15 (`ordertrack-postgres`), Redis 7 (`ordertrack-redis`) — plain `docker run` containers
- **Layering:** `routes (blueprints) → models (SQLAlchemy) → Postgres`, with Redis as a side cache for `/status`

---

## 1. System architecture diagram

```
                       ┌──────────────────────────────┐
                       │   Browser (React + Vite SPA)  │
                       │        http://:5173           │
                       └───────────────┬──────────────┘
                                       │ fetch /api/*  (CORS: allow all)
                                       ▼
            ┌─────────────────────────────────────────────────────┐
            │            Flask app  (create_app factory)           │
            │                  http://:8010                        │
            │                                                      │
            │   Blueprints (routes layer)                          │
            │   ┌─────────────┬───────────┬───────────┬─────────┐ │
            │   │ health_bp   │ orders_bp │ products  │customers│ │
            │   │ /api/health │/api/orders│/api/...   │/api/... │ │
            │   └──────┬──────┴─────┬─────┴─────┬─────┴────┬────┘ │
            │          │            │           │          │      │
            │          │      ┌─────▼────────┐  │          │      │
            │          │      │order_status. │  │          │      │
            │          │      │py (cache aside)│ │          │      │
            │          │      └──┬────────┬──┘  │          │      │
            │          │         │        │     │          │      │
            │     ┌────▼─────────▼────────▼─────▼──────────▼────┐ │
            │     │   models.py  (SQLAlchemy ORM / db session)  │ │
            │     │ Customer · Product · Order · OrderItem      │ │
            │     └────┬───────────────────────────────┬───────┘ │
            └──────────┼───────────────────────────────┼─────────┘
                       │                                │
              ┌────────▼─────────┐            ┌─────────▼────────┐
              │   PostgreSQL 15  │            │     Redis 7      │
              │  (system of      │            │  order_status:*  │
              │   record)        │            │  TTL=30s cache   │
              └──────────────────┘            └──────────────────┘
```

---

## 2. Data flow: request → service → DB

**Write path — `POST /api/orders` (create order):**
```
client ─JSON{customer_id,items[]}─▶ orders_bp.create_order
        ▶ validate customer_id + items present (400 if missing)
        ▶ for each item: Product.query.get(product_id)   ── Postgres SELECT
              └ snapshot product.price into OrderItem.unit_price
        ▶ db.session.add(order); db.session.commit()     ── Postgres INSERT (order + items)
        ◀ 201 order.to_dict()  (total computed from items)
```

**Read path with cache — `GET /api/orders/<id>/status`:**
```
client ──▶ orders_bp.order_status ──▶ order_status.get_order_status(id)
        1. GET order_status:<id>  ── Redis
              └ HIT  → return payload + source="cache"
        2. MISS → Order.query.get(id)  ── Postgres SELECT
              └ None → 404
        3. SETEX order_status:<id> TTL=30s  ── Redis (populate cache)
        ◀ payload {order_id,status,total} + source="db"
```

**Invalidation:** `PUT /api/orders/<id>` and `DELETE /api/orders/<id>` call
`invalidate_order_status(id)` → `DEL order_status:<id>` in Redis after commit,
so the next status read repopulates from Postgres.

---

## 3. Endpoints (every route, with HTTP method)

| Method | Path                        | Handler                  | Notes |
| ------ | --------------------------- | ------------------------ | ----- |
| GET    | `/api/health`               | `health.health`          | Checks Postgres `SELECT 1` + Redis `PING`; 503 if degraded |
| GET    | `/api/orders`               | `orders.list_orders`     | List all, ordered by id |
| POST   | `/api/orders`               | `orders.create_order`    | Requires `customer_id` + `items[]`; snapshots unit price; 201 |
| GET    | `/api/orders/<id>`          | `orders.get_order`       | 404 if missing |
| GET    | `/api/orders/<id>/status`   | `orders.order_status`    | Redis-cached status lookup |
| PUT    | `/api/orders/<id>`          | `orders.update_order`    | Updates `status` only (validated vs `ORDER_STATUSES`); invalidates cache |
| DELETE | `/api/orders/<id>`          | `orders.delete_order`    | Cascades to order_items; invalidates cache |
| GET    | `/api/products`             | `products.list_products` | |
| GET    | `/api/products/<id>`        | `products.get_product`   | 404 if missing |
| POST   | `/api/products`             | `products.create_product`| Requires `name` + `sku`; 201 |
| PUT    | `/api/products/<id>`        | `products.update_product`| Partial update |
| DELETE | `/api/products/<id>`        | `products.delete_product`| |
| GET    | `/api/customers`            | `customers.list_customers`| |
| GET    | `/api/customers/<id>`       | `customers.get_customer` | 404 if missing |
| POST   | `/api/customers`            | `customers.create_customer`| Requires `name` + `email`; 201 |
| PUT    | `/api/customers/<id>`       | `customers.update_customer`| Partial update |
| DELETE | `/api/customers/<id>`       | `customers.delete_customer`| |

Order lifecycle states: `pending → paid → shipped → delivered → cancelled`
(`ORDER_STATUSES`, no transition rules enforced).

---

## 4. Missing features vs production

**Security / AuthN-Z**
- No authentication or authorization — every endpoint is public.
- `CORS(app)` allows all origins.
- `SECRET_KEY` defaults to `dev-secret-key`; secrets only from env with dev defaults.
- No rate limiting, no input sanitization beyond presence checks.

**Data integrity / business logic**
- No stock decrement or validation on order creation (can order out-of-stock).
- No order-status transition rules (any status → any status).
- Email/SKU uniqueness enforced only at DB level → 500 on duplicate (no friendly 409).
- No pagination, filtering, or sorting on list endpoints.
- `db.create_all()` + `seed_data()` run on every boot — no real migrations (Alembic).

**Operational / reliability**
- No structured logging, request IDs, metrics, or tracing.
- No global error handling for SQLAlchemy/Redis exceptions (only 404/400 handlers).
- Redis treated as best-effort but no circuit breaking; cache stampede possible.
- Runs via `python wsgi.py` (dev server) — no Gunicorn/uWSGI for prod.
- No `docker-compose`; data stores are ad-hoc `docker run` containers.
- No CI/CD pipeline, no containerized backend image, no health-based deploy.
- No tests wired into a runner config visible here (test files exist under `tests/`).

---

## 5. Capstone implementation plan

Sequenced to match the lab's specialist-agent flow. Each phase is a discrete,
reviewable slice.

**Phase 1 — Auth & hardening (Security agent lane)**
1. Add `/api/auth/register` + `/api/auth/login` issuing JWT; an `auth.py` blueprint + `@require_auth` decorator.
2. Hash passwords (bcrypt), add a `users`/`customers.password_hash` column.
3. Lock down CORS to known origins; move `SECRET_KEY` to required env (fail fast if unset).
4. Add rate limiting (Flask-Limiter) and consistent JSON error envelope + 409 on uniqueness conflicts.

**Phase 2 — Business correctness (Architect + Reviewer lanes)**
5. Enforce stock checks + decrement stock atomically in `create_order` (within the transaction).
6. Enforce order-status transition rules (state machine over `ORDER_STATUSES`).
7. Add pagination/filtering to list endpoints.
8. Introduce a thin service layer (`services/`) so routes stay HTTP-only and rules are testable.

**Phase 3 — Persistence & infra**
9. Replace `create_all()`/`seed_data()` on boot with Alembic migrations + a seed CLI command.
10. Add `docker-compose.yml` (api + postgres + redis) and a backend `Dockerfile`; serve with Gunicorn.

**Phase 4 — Quality gates (Test agent lane)**
11. Flesh out pytest suite (unit for services, integration via test client; fixtures for db/redis).
12. Add coverage threshold + lint (flake8/black/bandit already in `.venv`).

**Phase 5 — CI/CD (per `notes.txt`)**
13. GitHub Actions: lint → test → security scan (bandit/safety) → build image.
14. CD to EC2 on green main; add PR-review + security-agent bots from the multi-agent lab.

**Phase 6 — Observability**
15. Structured logging w/ request IDs, `/metrics`, and richer `/api/health` (dependency latencies).
