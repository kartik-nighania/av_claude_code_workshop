"""Database connection helpers for the OrderTrack API."""
import os

from sqlalchemy import create_engine

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
