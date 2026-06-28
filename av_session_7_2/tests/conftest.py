"""Shared pytest fixtures for the OrderTrack API test suite.

The app is run against an in-memory SQLite database (no Postgres needed) and
with Redis disabled, so `order_status` transparently degrades to DB-only reads.
"""

from datetime import datetime, timedelta

import jwt
import pytest
from sqlalchemy.pool import StaticPool

import app.seed as seed_module
from app import create_app
from app.config import Config
from app.extensions import _RedisHolder, db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"  # in-memory
    # Keep the single in-memory connection alive across the test's requests.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    SECRET_KEY = "test-secret-key"
    ORDER_STATUS_CACHE_TTL = 30


@pytest.fixture
def app(monkeypatch):
    # Tests manage their own data; skip the demo seed.
    monkeypatch.setattr(seed_module, "seed_data", lambda: None)

    application = create_app(TestConfig)

    # Disable Redis: get_redis() now returns None everywhere (null-safe paths).
    _RedisHolder.client = None

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# --- auth helpers ----------------------------------------------------------


@pytest.fixture
def user(client):
    """Register a user and return identity + ready-to-use auth headers."""
    email = "tester@example.com"
    password = "password123"
    resp = client.post("/auth/register", json={"email": email, "password": password})
    assert resp.status_code == 201, resp.get_json()
    token = resp.get_json()["access_token"]
    return {
        "email": email,
        "password": password,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def auth_headers(user):
    return user["headers"]


@pytest.fixture
def expired_token(app):
    """A structurally-valid JWT whose exp is in the past."""
    with app.app_context():
        now = datetime.utcnow()
        return jwt.encode(
            {
                "sub": 1,
                "email": "ghost@example.com",
                "iat": now - timedelta(hours=25),
                "exp": now - timedelta(hours=1),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )


# --- data helpers ----------------------------------------------------------


@pytest.fixture
def make_customer(client):
    def _make(name="Alice", email="alice@example.com"):
        resp = client.post("/api/customers", json={"name": name, "email": email})
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()

    return _make


@pytest.fixture
def make_product(client, auth_headers):
    def _make(name="Widget", sku="WGT-001", price=9.99, stock=100):
        resp = client.post(
            "/api/products",
            json={"name": name, "sku": sku, "price": price, "stock": stock},
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()

    return _make
