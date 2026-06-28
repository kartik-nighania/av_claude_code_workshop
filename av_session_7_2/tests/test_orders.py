"""CRUD + status for /api/orders (auth-protected) — happy paths + negatives."""


def _order_payload(customer_id, product_id, quantity=2):
    return {
        "customer_id": customer_id,
        "items": [{"product_id": product_id, "quantity": quantity}],
    }


def test_list_orders_requires_auth(client):
    assert client.get("/api/orders").status_code == 401


def test_create_order(client, auth_headers, make_customer, make_product):
    customer = make_customer()
    product = make_product(price=10.0)
    resp = client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product["id"], quantity=3),
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["customer_id"] == customer["id"]
    assert body["status"] == "pending"
    assert body["total"] == 30.0  # 3 * 10.00, unit_price snapshotted from product
    assert len(body["items"]) == 1


def test_create_order_missing_fields_400(client, auth_headers):
    resp = client.post("/api/orders", json={"customer_id": 1}, headers=auth_headers)
    assert resp.status_code == 400


def test_create_order_unknown_product_400(client, auth_headers, make_customer):
    customer = make_customer()
    resp = client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product_id=9999),
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_create_order_unauthorized_401(client):
    resp = client.post("/api/orders", json=_order_payload(1, 1))
    assert resp.status_code == 401


def test_get_order(client, auth_headers, make_customer, make_product):
    customer = make_customer()
    product = make_product()
    created = client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product["id"]),
        headers=auth_headers,
    ).get_json()
    resp = client.get(f"/api/orders/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == created["id"]


def test_get_order_404(client, auth_headers):
    resp = client.get("/api/orders/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_order_status_lookup(client, auth_headers, make_customer, make_product):
    customer = make_customer()
    product = make_product()
    created = client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product["id"]),
        headers=auth_headers,
    ).get_json()
    resp = client.get(f"/api/orders/{created['id']}/status", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["order_id"] == created["id"]
    assert body["status"] == "pending"
    assert body["source"] == "db"  # Redis disabled in tests → always DB


def test_order_status_404(client, auth_headers):
    resp = client.get("/api/orders/9999/status", headers=auth_headers)
    assert resp.status_code == 404


def test_update_order_status(client, auth_headers, make_customer, make_product):
    customer = make_customer()
    product = make_product()
    created = client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product["id"]),
        headers=auth_headers,
    ).get_json()
    resp = client.put(
        f"/api/orders/{created['id']}",
        json={"status": "shipped"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "shipped"


def test_update_order_invalid_status_400(
    client, auth_headers, make_customer, make_product
):
    customer = make_customer()
    product = make_product()
    created = client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product["id"]),
        headers=auth_headers,
    ).get_json()
    resp = client.put(
        f"/api/orders/{created['id']}",
        json={"status": "teleported"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_update_order_404(client, auth_headers):
    resp = client.put("/api/orders/9999", json={"status": "paid"}, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_order(client, auth_headers, make_customer, make_product):
    customer = make_customer()
    product = make_product()
    created = client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product["id"]),
        headers=auth_headers,
    ).get_json()
    resp = client.delete(f"/api/orders/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == created["id"]
    assert (
        client.get(f"/api/orders/{created['id']}", headers=auth_headers).status_code
        == 404
    )


def test_delete_order_404(client, auth_headers):
    resp = client.delete("/api/orders/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_list_orders(client, auth_headers, make_customer, make_product):
    customer = make_customer()
    product = make_product()
    client.post(
        "/api/orders",
        json=_order_payload(customer["id"], product["id"]),
        headers=auth_headers,
    )
    resp = client.get("/api/orders", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1
