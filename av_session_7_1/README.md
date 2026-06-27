# OrderTrack API

A Python / Flask e-commerce backend — **currently broken, insecure & ungoverned.**
This is a teaching sandbox: the bugs below are intentional. The mission is to
**debug it · secure it · document it** with Claude Code.

| | |
| --- | --- |
| **Stack** | Python 3.11 · Flask · PostgreSQL · Redis |
| **Endpoints** | Orders, Products, Customers, Inventory |
| **Current state** | 3 failing endpoints · 5 security holes · zero governance docs |
| **Frontend** | React 18 + Vite |

## Run it

### Full stack (Docker)

Postgres + Redis + Flask API + React UI together:

```bash
# 1. Build and start everything
docker compose up --build

# 2. Open the UI
open http://localhost:5174        # API: http://localhost:8000/api/health
```

### Backend locally (Flask CLI)

```bash
cd ordertrack-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Start the app   (binds port 8000 via .flaskenv)
flask run

# 2. Collect the error
flask run 2>&1 | head -40
```

`flask run` picks up `.flaskenv` (`FLASK_APP=app`, `FLASK_RUN_PORT=8000`) and
`.env`. The app boots even when PostgreSQL is unreachable — the failure shows up
when a request actually touches the database, e.g. `GET /api/orders` returns a
500 with `sqlalchemy.exc.OperationalError ... port 5432`.

To back the local API with a database, start one from Docker and seed it once:

```bash
docker compose up -d db redis
python seed.py
```

Run the tests (needs the API running):

```bash
cd ordertrack-api
pytest tests/test_orders.py
pytest tests/test_api.py
```

## Endpoints

| Method | Path | Notes |
| --- | --- | --- |
| GET  | `/api/health` | liveness |
| POST | `/api/auth/login` | returns a token (`admin` / `admin123`) |
| GET  | `/api/orders` | list orders |
| GET  | `/api/orders/search?customer_name=` | search by customer |
| POST | `/api/orders` | create an order |
| GET  | `/api/products` | list products (auth) |
| GET  | `/api/customers` | list customers (auth) |
| GET  | `/api/inventory` | list inventory (auth) |
| GET  | `/api/admin/users` | admin user dump |

## Mission

Debug it · Secure it · Document it — all with Claude Code.
