"""Products CRUD. All routes require auth."""


def test_list_products(client, auth_headers):
    resp = client.get("/api/products", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1  # seeded products


def test_get_product(client, auth_headers):
    resp = client.get("/api/products/1", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == 1


def test_get_product_404(client, auth_headers):
    assert client.get("/api/products/9999", headers=auth_headers).status_code == 404


def test_create_product(client, auth_headers):
    resp = client.post(
        "/api/products",
        headers=auth_headers,
        json={"name": "Doohickey", "sku": "DHK-009", "price": 12.5, "stock": 7},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Doohickey"
    assert body["sku"] == "DHK-009"


def test_create_product_missing_fields_400(client, auth_headers):
    resp = client.post("/api/products", headers=auth_headers, json={"name": "No SKU"})
    assert resp.status_code == 400


def test_update_product(client, auth_headers):
    resp = client.put(
        "/api/products/1", headers=auth_headers, json={"price": 99.99, "stock": 5}
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["price"] == 99.99
    assert body["stock"] == 5


def test_update_product_404(client, auth_headers):
    resp = client.put("/api/products/9999", headers=auth_headers, json={"price": 1})
    assert resp.status_code == 404


def test_delete_product(client, auth_headers):
    assert client.delete("/api/products/1", headers=auth_headers).status_code == 200
    assert client.get("/api/products/1", headers=auth_headers).status_code == 404


def test_products_require_auth(client):
    assert client.get("/api/products").status_code == 401
