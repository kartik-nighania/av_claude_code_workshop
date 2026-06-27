"""Order persistence and queries for the OrderTrack API.

Reads and writes for the ``orders`` table. The search/fetch/create helpers
share a small SQLAlchemy connection; the list endpoint opens its own direct
psycopg2 connection.

Connection details (host, port, database) come from environment variables and
are resolved on each call.
"""
import os

import psycopg2
from sqlalchemy import create_engine, text

from db import DATABASE_URL
from utils.logger import get_logger

log = get_logger("order_service")


def _connect():
    engine = create_engine(DATABASE_URL)
    return engine.connect()


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


def get_orders(customer_id):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    )
    cur = conn.cursor()
    if customer_id:
        cur.execute(
            "SELECT * FROM orders WHERE customer_id = %s ORDER BY id", (customer_id,)
        )
    else:
        cur.execute("SELECT * FROM orders ORDER BY id")
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows


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
