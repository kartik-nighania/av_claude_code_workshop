"""Basic application config.

NOTE: secrets handling is intentionally minimal for this demo — values come
from env vars with local-dev defaults. Do not ship these defaults.
"""
import os


class Config:
    # Postgres (db service: postgres:15-alpine)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://ordertrack:ordertrack@localhost:5432/ordertrack",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis (cache service: redis:7-alpine)
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Plain default secret — fine for the demo, not for production.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # How long (seconds) to cache a computed order status in Redis.
    ORDER_STATUS_CACHE_TTL = int(os.environ.get("ORDER_STATUS_CACHE_TTL", "30"))
