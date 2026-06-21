"""Shared extension singletons for the HealthTrack API."""
import os

import redis
from flask_sqlalchemy import SQLAlchemy

# Database handle — bound to the app inside create_app().
db = SQLAlchemy()

# Redis cache client. redis.from_url() is lazy: no socket is opened until the
# first command runs, so it is safe to build at import time even if the cache
# container is not up yet (the /health route pings it explicitly).
cache = redis.from_url(os.environ.get("REDIS_URL", "redis://cache:6379/0"))
