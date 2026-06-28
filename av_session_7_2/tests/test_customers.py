"""Customers CRUD. These routes are NOT auth-protected."""


def test_list_customers(client):
    resp = client.get("/api/customers")
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1  # seeded customers


def test_get_customer(client):
    resp = client.get("/api/customers/1")
    assert resp.status_code == 200
    assert resp.get_json()["id"] == 1


def test_get_customer_404(client):
    assert client.get("/api/customers/9999").status_code == 404


def test_create_customer(client):
    resp = client.post(
        "/api/customers", json={"name": "Carol", "email": "carol@example.com"}
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Carol"
    assert body["email"] == "carol@example.com"


def test_create_customer_missing_fields_400(client):
    resp = client.post("/api/customers", json={"name": "No Email"})
    assert resp.status_code == 400


def test_update_customer(client):
    resp = client.put("/api/customers/1", json={"name": "Renamed"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Renamed"


def test_update_customer_404(client):
    assert client.put("/api/customers/9999", json={"name": "X"}).status_code == 404


def test_delete_customer(client):
    assert client.delete("/api/customers/2").status_code == 200
    assert client.get("/api/customers/2").status_code == 404
