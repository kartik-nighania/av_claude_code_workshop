"""Health check — unprotected, reports DB + Redis status."""


def test_health_ok(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"
    assert body["redis"] == "ok"


def test_health_needs_no_auth(client):
    # No Authorization header is required.
    assert client.get("/api/health").status_code == 200


def test_unknown_route_404(client):
    assert client.get("/api/nope").status_code == 404
