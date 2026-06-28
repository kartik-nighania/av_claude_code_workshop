"""CRUD for /api/customers (unprotected) — happy paths + negative cases."""


def test_list_customers_empty(client):
    resp = client.get("/api/customers")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_customer(client):
    resp = client.post(
        "/api/customers", json={"name": "Alice", "email": "alice@example.com"}
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["id"]
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"


def test_create_customer_missing_fields_400(client):
    resp = client.post("/api/customers", json={"name": "NoEmail"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_get_customer(client, make_customer):
    created = make_customer()
    resp = client.get(f"/api/customers/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["email"] == created["email"]


def test_get_customer_404(client):
    resp = client.get("/api/customers/9999")
    assert resp.status_code == 404


def test_update_customer(client, make_customer):
    created = make_customer()
    resp = client.put(f"/api/customers/{created['id']}", json={"name": "Alice Updated"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Alice Updated"


def test_update_customer_404(client):
    resp = client.put("/api/customers/9999", json={"name": "Ghost"})
    assert resp.status_code == 404


def test_delete_customer(client, make_customer):
    created = make_customer()
    resp = client.delete(f"/api/customers/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == created["id"]
    assert client.get(f"/api/customers/{created['id']}").status_code == 404


def test_delete_customer_404(client):
    resp = client.delete("/api/customers/9999")
    assert resp.status_code == 404
