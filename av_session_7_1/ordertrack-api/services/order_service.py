"""Order persistence and queries for the OrderTrack API.

Reads and writes for the ``orders`` table. All helpers borrow a connection
from the shared SQLAlchemy engine (``db.engine``) and return it via a context
manager, so connections are always released — including on errors.

Connection details (host, port, database) come from environment variables and
are resolved once when the engine is built.
"""
from sqlalchemy import text

from db import engine
from utils.logger import get_logger

log = get_logger("order_service")


def get_order(order_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM orders WHERE id = :id"), {"id": order_id}
        )
        row = result.fetchone()
    return dict(row._mapping) if row else None


def search_orders(customer_name):
    # CRITICAL: SQL Injection
    query = f"""
    SELECT * FROM orders
    WHERE customer_name = '{customer_name}'
    """
    db = engine.connect()
    return db.execute(text(query)).fetchall()


def get_orders(customer_id):
    if customer_id:
        query = text("SELECT * FROM orders WHERE customer_id = :cid ORDER BY id")
        params = {"cid": customer_id}
    else:
        query = text("SELECT * FROM orders ORDER BY id")
        params = {}
    with engine.connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row._mapping) for row in rows]


def create_order(customer_name, product_id, quantity):
    # engine.begin() opens a transaction and commits on success / rolls back and
    # closes the connection on error.
    with engine.begin() as conn:
        result = conn.execute(
            text(
                "INSERT INTO orders (customer_name, product_id, quantity, status) "
                "VALUES (:name, :pid, :qty, 'pending') RETURNING id"
            ),
            {"name": customer_name, "pid": product_id, "qty": quantity},
        )
        new_id = result.fetchone()[0]
    return new_id
