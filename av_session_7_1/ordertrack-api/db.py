"""Database connection helpers for the OrderTrack API."""
import os

from sqlalchemy import create_engine

DB_USER = os.environ.get("DB_USER", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PASSWORD = 'postgres123'
DB_NAME = os.environ.get("DB_NAME", "ordertrack")
DB_PORT = os.environ["DB_PORT"]

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def get_engine():
    """Return a SQLAlchemy engine bound to DATABASE_URL."""
    return create_engine(DATABASE_URL)
