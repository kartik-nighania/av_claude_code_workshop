# OrderTrack API

A small order-tracking demo: a Flask REST API backed by PostgreSQL and Redis,
with a React (Vite) frontend.

> **Status:** starter scaffold. Basic CRUD only.

## Stack

- **Backend:** Flask + SQLAlchemy (`app/`), served on `:8010`
- **Frontend:** React + Vite (`frontend/`), served on `:5173`
- **Data:** PostgreSQL 15 (`db`) and Redis 7 (`cache`), run as Docker containers

## Run it

```bash
./startup.sh
```

This starts the Postgres and Redis containers (creating them if needed), then
runs the backend and frontend. Open http://localhost:5173.

## Endpoints

| Method | Path                        | Description                |
| ------ | --------------------------- | -------------------------- |
| GET    | `/api/health`               | DB + Redis health          |
| GET    | `/api/orders`               | List orders                |
| POST   | `/api/orders`               | Create an order            |
| GET    | `/api/orders/<id>`          | Get one order              |
| PUT    | `/api/orders/<id>`          | Update order status        |
| DELETE | `/api/orders/<id>`          | Delete an order            |
| GET    | `/api/orders/<id>/status`   | Cached order status        |
| GET/POST/PUT/DELETE | `/api/products`    | Product CRUD               |
| GET/POST/PUT/DELETE | `/api/customers`   | Customer CRUD              |

Order status reads go through `app/order_status.py:get_order_status`, which
caches results in Redis.

## Config

Copy `.env.example` to `.env` to override defaults (`DATABASE_URL`, `REDIS_URL`,
`PORT`, ...).

<!-- TODO: deployment, auth, tests -->
