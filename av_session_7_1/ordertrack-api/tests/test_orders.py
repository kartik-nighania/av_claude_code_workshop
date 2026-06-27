"""Order endpoint tests.

Run with:  pytest tests/test_orders.py
Requires a running instance on http://localhost:8000 with a seeded database.
"""
import requests

BASE_URL = "http://localhost:8000"


def test_list_orders_returns_list():
    resp = requests.get(f"{BASE_URL}/api/orders")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_search_orders_by_customer():
    resp = requests.get(
        f"{BASE_URL}/api/orders/search", params={"customer_name": "Alice Johnson"}
    )
    assert resp.status_code == 200


def test_create_order_missing_field_returns_400():
    resp = requests.post(
        f"{BASE_URL}/api/orders",
        json={"customer_name": "Alice Johnson", "product_id": 1},
    )
    assert resp.status_code == 400
