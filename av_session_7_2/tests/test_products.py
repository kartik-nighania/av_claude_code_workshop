"""CRUD for /api/products (auth-protected) — happy paths + negative cases."""


def test_list_products_requires_auth(client):
    assert client.get("/api/products").status_code == 401


def test_list_products_empty(client, auth_headers):
    resp = client.get("/api/products", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_product(client, auth_headers):
    resp = client.post(
        "/api/products",
        json={"name": "Gadget", "sku": "GDG-002", "price": 24.5, "stock": 40},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Gadget"
    assert body["sku"] == "GDG-002"
    assert body["price"] == 24.5
    assert body["stock"] == 40


def test_create_product_missing_fields_400(client, auth_headers):
    resp = client.post(
        "/api/products", json={"name": "NoSku"}, headers=auth_headers
    )
    assert resp.status_code == 400


def test_create_product_unauthorized_401(client):
    resp = client.post("/api/products", json={"name": "X", "sku": "X-1"})
    assert resp.status_code == 401


def test_get_product(client, auth_headers, make_product):
    created = make_product()
    resp = client.get(f"/api/products/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["sku"] == created["sku"]


def test_get_product_404(client, auth_headers):
    resp = client.get("/api/products/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_product(client, auth_headers, make_product):
    created = make_product()
    resp = client.put(
        f"/api/products/{created['id']}",
        json={"price": 12.0, "stock": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["price"] == 12.0
    assert body["stock"] == 5


def test_delete_product(client, auth_headers, make_product):
    created = make_product()
    resp = client.delete(f"/api/products/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == created["id"]
    assert (
        client.get(f"/api/products/{created['id']}", headers=auth_headers).status_code
        == 404
    )


def test_delete_product_404(client, auth_headers):
    resp = client.delete("/api/products/9999", headers=auth_headers)
    assert resp.status_code == 404
