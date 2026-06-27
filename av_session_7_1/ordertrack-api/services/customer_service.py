"""Customer business logic."""
from sqlalchemy import text

from db import get_engine

_engine = get_engine()


def get_customers():
    with _engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, name, email, created_at FROM customers ORDER BY id")
        )
        return [dict(r._mapping) for r in result.fetchall()]


def get_customer(customer_id):
    with _engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, name, email, created_at FROM customers WHERE id = :id"),
            {"id": customer_id},
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None
