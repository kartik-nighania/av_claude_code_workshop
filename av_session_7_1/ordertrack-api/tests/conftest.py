"""Shared pytest fixtures for the OrderTrack API test suite.

Loads the project's ``.env`` so the tests see exactly the configuration the
running app sees (same DB_HOST/DB_PORT/...). ``load_dotenv`` does not override
variables already present in the environment, so values injected by Docker
(``DB_HOST=db`` etc.) still win when the suite runs inside a container.
"""
import os

import pytest
from dotenv import load_dotenv

# Resolve <repo>/ordertrack-api/.env relative to this file and load it before
# importing anything that reads DB_* at import time (db.py builds the engine URL
# the moment it is imported).
_ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(_ENV_PATH)

import db  # noqa: E402  (must come after load_dotenv)
from app import app as flask_app  # noqa: E402


def database_reachable():
    """True when the configured database answers a SELECT 1."""
    return db.ping()


@pytest.fixture(scope="session")
def db_engine():
    """The shared SQLAlchemy engine, configured exactly as the app uses it."""
    return db.get_engine()


@pytest.fixture()
def client():
    """Flask test client for hitting routes without a live server."""
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()


@pytest.fixture()
def require_db():
    """Skip (loudly) when no database is reachable.

    Integration tests depend on it so the suite still runs in a DB-less
    environment instead of failing with connection errors.
    """
    if not database_reachable():
        pytest.skip(
            "database not reachable at "
            f"{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')} — "
            "start it with `docker compose up -d db`"
        )
