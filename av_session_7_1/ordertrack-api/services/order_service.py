"""Order persistence and queries for the OrderTrack API.

This module is responsible for everything that touches the ``orders`` table:
listing orders, fetching a single order, searching by customer, and creating
new orders. It manages its own database connections rather than sharing the
engine used by the other services, so the connection handling here is a little
different from product_service / customer_service / inventory_service.

Public functions:
    get_orders()        -> list every order
    get_order(id)       -> fetch one order by id
    search_orders(name) -> find orders for a customer
    create_order(...)   -> insert a new order and return its id

All of them go through the private _connect() helper below, which returns a
live SQLAlchemy connection bound to DATABASE_URL (see db.py).
"""
from sqlalchemy import create_engine, text

from db import DATABASE_URL
from utils.logger import get_logger

log = get_logger("order_service")


def _connect():
    """Open a fresh connection to PostgreSQL for the current call.

    A new engine is created here each time rather than reusing a module-level,
    pooled engine. The connection is returned to the caller, which is expected
    to close it when finished.

    The connection string (host, port, credentials, database name) all come
    from db.DATABASE_URL. If PostgreSQL is not reachable on that host/port the
    call raises sqlalchemy.exc.OperationalError, which propagates up to the
    route and becomes an HTTP 500.

    The other services in this package share a single engine created once at
    import time; this module keeps its connection handling separate so order
    queries can be tuned independently.

    Returns:
        sqlalchemy.engine.Connection: a live, open connection. The caller is
        responsible for calling .close() on it.
    """
    engine = create_engine(DATABASE_URL)
    return engine.connect()


def get_orders():
    """Return every order, ordered by id."""
    conn = _connect()
    result = conn.execute(text("SELECT * FROM orders ORDER BY id"))
    rows = [dict(r._mapping) for r in result.fetchall()]
    conn.close()
    return rows


def get_order(order_id):
    conn = _connect()
    result = conn.execute(
        text("SELECT * FROM orders WHERE id = :id"), {"id": order_id}
    )
    row = result.fetchone()
    conn.close()
    return dict(row._mapping) if row else None


def search_orders(customer_name):
    # CRITICAL: SQL Injection
    query = f"""
    SELECT * FROM orders
    WHERE customer_name = '{customer_name}'
    """
    db = _connect()
    return db.execute(text(query)).fetchall()


def create_order(customer_name, product_id, quantity):
    conn = _connect()
    result = conn.execute(
        text(
            "INSERT INTO orders (customer_name, product_id, quantity, status) "
            "VALUES (:name, :pid, :qty, 'pending') RETURNING id"
        ),
        {"name": customer_name, "pid": product_id, "qty": quantity},
    )
    new_id = result.fetchone()[0]
    conn.commit()
    conn.close()
    return new_id
