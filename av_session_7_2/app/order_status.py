"""Order status lookup with a Redis-backed cache.

`get_order_status` is the canonical way to read an order's current status:
it checks Redis first and falls back to Postgres, caching the result.
"""
import json

from flask import current_app

from .extensions import get_redis
from .models import Order

_CACHE_PREFIX = "order_status:"


def get_order_status(order_id):
    """Return the status for an order, or None if the order does not exist.

    Result shape:
        {"order_id": int, "status": str, "total": float, "source": "cache"|"db"}
    """
    cache = get_redis()
    cache_key = f"{_CACHE_PREFIX}{order_id}"

    if cache is not None:
        cached = cache.get(cache_key)
        if cached:
            payload = json.loads(cached)
            payload["source"] = "cache"
            return payload

    order = Order.query.get(order_id)
    if order is None:
        return None

    payload = {
        "order_id": order.id,
        "status": order.status,
        "total": round(order.total, 2),
    }

    if cache is not None:
        ttl = current_app.config.get("ORDER_STATUS_CACHE_TTL", 30)
        cache.setex(cache_key, ttl, json.dumps(payload))

    result = dict(payload)
    result["source"] = "db"
    return result


def invalidate_order_status(order_id):
    """Drop the cached status for an order (call after a status change)."""
    cache = get_redis()
    if cache is not None:
        cache.delete(f"{_CACHE_PREFIX}{order_id}")
