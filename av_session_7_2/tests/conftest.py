"""Shared pytest fixtures.

The app is built with an in-memory SQLite DB (no Postgres needed) and a tiny
in-process fake Redis (no Redis server needed), so the whole suite runs hermetic.
"""

from datetime import datetime, timedelta

import jwt
import pytest
from sqlalchemy.pool import StaticPool

from app import create_app, extensions
from app.auth import hash_password, make_token
from app.config import Config
from app.extensions import db
from app.models import User


class TestConfig(Config):
    TESTING = True
    # A single shared in-memory SQLite connection (StaticPool keeps the same
    # connection so the schema + seed data persist across requests).
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    SECRET_KEY = "test-secret"
    ORDER_STATUS_CACHE_TTL = 30


class FakeRedis:
    """Minimal Redis stand-in covering the calls the app makes."""

    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, _ttl, value):
        self.store[key] = value

    def delete(self, key):
        self.store.pop(key, None)

    def ping(self):
        return True


@pytest.fixture
def app():
    application = create_app(TestConfig)
    # Swap the (lazy) real Redis client for the fake after the app is built.
    extensions._RedisHolder.client = FakeRedis()
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    """A persisted user; returns plain values (detached after the context)."""
    with app.app_context():
        u = User(
            name="Test User",
            email="test@example.com",
            hashed_password=hash_password("password123"),
        )
        db.session.add(u)
        db.session.commit()
        return {"id": u.id, "email": u.email, "password": "password123"}


@pytest.fixture
def auth_headers(app, user):
    """Authorization header carrying a valid bearer token for `user`."""
    with app.app_context():
        token = make_token(User.query.get(user["id"]))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def expired_headers(app, user):
    """Authorization header with a token whose exp is in the past."""
    with app.app_context():
        token = jwt.encode(
            {
                "sub": str(user["id"]),
                "exp": datetime.utcnow() - timedelta(hours=1),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
    return {"Authorization": f"Bearer {token}"}
