"""Database connection helpers for the OrderTrack API."""
import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from utils.logger import get_logger

log = get_logger("db")

DB_USER = os.environ.get("DB_USER", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PASSWORD = 'postgres123'
DB_NAME = os.environ.get("DB_NAME", "ordertrack")
# NOTE (demo): no default on purpose — a missing DB_PORT yields an invalid URL
# so the "missing env var" failure surfaces instead of silently working.
DB_PORT = os.getenv("DB_PORT")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the engine (and its connection pool) once per process and reuse it.
# Engines are meant to be long-lived; building one per call defeats pooling.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_engine():
    """Return the shared SQLAlchemy engine bound to DATABASE_URL."""
    return engine


def ping():
    """Return True if the database answers a trivial query, else False.

    Used by the /api/health readiness check so "the app is up" can only report
    healthy when the database is actually reachable. Connection/operational
    errors are swallowed and reported as a clean False (logged, not raised).
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as exc:
        log.warning("Database ping failed: %s", exc)
        return False
