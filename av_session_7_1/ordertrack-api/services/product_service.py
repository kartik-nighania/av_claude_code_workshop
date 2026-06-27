"""Product business logic."""
from sqlalchemy import text

from db import get_engine

# Shared engine, created once at import.
_engine = get_engine()


def get_products():
    with _engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM products ORDER BY id"))
        return [dict(r._mapping) for r in result.fetchall()]


def get_product(product_id):
    with _engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM products WHERE id = :id"), {"id": product_id}
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None
