"""Orders CRUD + cached status. All routes require auth."""


def test_list_orders(client, auth_headers):
    resp = client.get("/api/orders", headers=auth_headers)
    assert resp.status_code == 200
    # Seed data includes one order.
    assert len(resp.get_json()) >= 1


def test_get_order(client, auth_headers):
    resp = client.get("/api/orders/1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == 1


def test_get_order_404(client, auth_headers):
    assert client.get("/api/orders/9999", headers=auth_headers).status_code == 404


def test_create_order(client, auth_headers):
    resp = client.post(
        "/api/orders",
        headers=auth_headers,
        json={"customer_id": 1, "items": [{"product_id": 1, "quantity": 3}]},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["customer_id"] == 1
    assert len(body["items"]) == 1
    assert body["total"] > 0


def test_create_order_missing_fields_400(client, auth_headers):
    resp = client.post("/api/orders", headers=auth_headers, json={"customer_id": 1})
    assert resp.status_code == 400


def test_create_order_unknown_product_400(client, auth_headers):
    resp = client.post(
        "/api/orders",
        headers=auth_headers,
        json={"customer_id": 1, "items": [{"product_id": 9999, "quantity": 1}]},
    )
    assert resp.status_code == 400


def test_update_order_status(client, auth_headers):
    resp = client.put("/api/orders/1", headers=auth_headers, json={"status": "shipped"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "shipped"


def test_update_order_invalid_status_400(client, auth_headers):
    resp = client.put(
        "/api/orders/1", headers=auth_headers, json={"status": "teleported"}
    )
    assert resp.status_code == 400


def test_update_order_404(client, auth_headers):
    resp = client.put("/api/orders/9999", headers=auth_headers, json={"status": "paid"})
    assert resp.status_code == 404


def test_order_status_cache_then_db(client, auth_headers):
    # First read populates the cache from the DB...
    first = client.get("/api/orders/1/status", headers=auth_headers)
    assert first.status_code == 200
    assert first.get_json()["source"] == "db"
    # ...second read is served from cache.
    second = client.get("/api/orders/1/status", headers=auth_headers)
    assert second.get_json()["source"] == "cache"


def test_order_status_404(client, auth_headers):
    resp = client.get("/api/orders/9999/status", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_order(client, auth_headers):
    assert client.delete("/api/orders/1", headers=auth_headers).status_code == 200
    assert client.get("/api/orders/1", headers=auth_headers).status_code == 404


def test_orders_require_auth(client):
    assert client.post("/api/orders", json={}).status_code == 401
