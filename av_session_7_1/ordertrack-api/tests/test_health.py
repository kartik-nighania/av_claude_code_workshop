"""/api/health reflects real database readiness.

The point of this lab fix: when the application reports healthy, the database
is genuinely reachable. "DB is up when the app is up" is *verified through the
health endpoint*, not assumed.
"""
import pytest


def test_health_endpoint_is_served(client):
    """Liveness: the route responds and self-identifies, whatever the DB state."""
    resp = client.get("/api/health")
    assert resp.status_code in (200, 503)
    body = resp.get_json()
    assert body["service"] == "ordertrack-api"
    # Health must surface DB status rather than hide it.
    assert body["db"] in ("ok", "down")


@pytest.mark.integration
@pytest.mark.usefixtures("require_db")
def test_health_ok_implies_db_up(client):
    """With a live DB, health is 200/ok and reports db=ok — app-up ⇒ db-up."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"


def test_health_degrades_when_db_down(client, monkeypatch):
    """If the DB ping fails, health must degrade to 503/down — never a false ok.

    Patches the ping used by the route so this runs without (and regardless of)
    a real database.
    """
    import app as app_module

    monkeypatch.setattr(app_module, "db_ping", lambda: False)

    resp = client.get("/api/health")
    assert resp.status_code == 503
    body = resp.get_json()
    assert body["status"] == "degraded"
    assert body["db"] == "down"
