"""The database is correctly wired and actually reachable.

Two layers:

* **Config tests** (always run) guard the wiring — that the engine URL is built
  from DB_PORT and that the port matches the one this project's Postgres really
  listens on (5433). This is the exact regression that bit us: a stale
  DB_PORT=5432 pointing at a server bound to 5433.
* **Integration tests** (``@pytest.mark.integration``) prove a live database
  answers queries and has been seeded. They skip — loudly — when no DB is up.
"""
import os

import pytest
from sqlalchemy import text

import db


# --------------------------------------------------------------------------- #
# Config / wiring — no database required
# --------------------------------------------------------------------------- #

def test_database_url_embeds_configured_port():
    """The engine URL must come from DB_PORT, not a hardcoded value."""
    port = os.environ.get("DB_PORT")
    assert port, "DB_PORT must be set (see .env / .env.example)"
    assert f":{port}/" in db.DATABASE_URL, db.DATABASE_URL


def test_configured_port_is_project_postgres_port():
    """Postgres runs on 5433 here, not the default 5432.

    Regression guard for the port mismatch fixed in this session — keep .env,
    .env.example and docker-compose all pointing at 5433.
    """
    assert os.environ.get("DB_PORT") == "5433", (
        "DB_PORT should be 5433 to match the project's Postgres; "
        f"got {os.environ.get('DB_PORT')!r}"
    )


def test_database_url_is_well_formed():
    """Sanity: the URL has host, port and database name (no None leaking in)."""
    assert db.DATABASE_URL.startswith("postgresql://")
    assert "None" not in db.DATABASE_URL, "a DB_* env var resolved to None"


# --------------------------------------------------------------------------- #
# Integration — needs a live database
# --------------------------------------------------------------------------- #

@pytest.mark.integration
@pytest.mark.usefixtures("require_db")
class TestLiveDatabase:
    def test_engine_connects_and_answers(self, db_engine):
        with db_engine.connect() as conn:
            assert conn.execute(text("SELECT 1")).scalar() == 1

    def test_ping_reports_up(self):
        assert db.ping() is True

    def test_connected_to_expected_port(self, db_engine):
        """The live connection is really on the configured port (not a default)."""
        with db_engine.connect() as conn:
            port = conn.execute(
                text("SELECT setting FROM pg_settings WHERE name = 'port'")
            ).scalar()
        assert str(port) == os.environ.get("DB_PORT")

    def test_seeded_tables_exist(self, db_engine):
        """seed.py / models.Base created the core tables the API reads from."""
        expected = {"customers", "products", "inventory", "orders"}
        with db_engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )).fetchall()
        present = {r[0] for r in rows}
        assert expected.issubset(present), f"missing tables: {expected - present}"
