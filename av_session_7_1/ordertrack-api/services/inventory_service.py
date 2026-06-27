"""Inventory business logic."""
from sqlalchemy import text

from db import get_engine

_engine = get_engine()


def get_inventory():
    with _engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT i.id, i.product_id, p.name AS product_name, "
                "i.quantity, i.warehouse "
                "FROM inventory i JOIN products p ON p.id = i.product_id "
                "ORDER BY i.id"
            )
        )
        return [dict(r._mapping) for r in result.fetchall()]


def adjust_inventory(product_id, delta):
    with _engine.connect() as conn:
        conn.execute(
            text(
                "UPDATE inventory SET quantity = quantity + :delta "
                "WHERE product_id = :pid"
            ),
            {"delta": delta, "pid": product_id},
        )
        conn.commit()
    return get_inventory()
