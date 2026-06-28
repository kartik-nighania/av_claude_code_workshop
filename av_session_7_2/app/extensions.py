"""Shared extension instances: SQLAlchemy (Postgres) and a Redis client."""

import redis
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class _RedisHolder:
    """Holds the process-wide Redis client, configured from app config."""

    client = None


def init_redis(app):
    _RedisHolder.client = redis.from_url(app.config["REDIS_URL"], decode_responses=True)


def get_redis():
    return _RedisHolder.client
