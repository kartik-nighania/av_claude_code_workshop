"""API smoke tests for the OrderTrack API.

Run with:  pytest tests/test_api.py
These hit a running instance on http://localhost:8000.
"""
import requests

BASE_URL = "http://localhost:8000"


def _login():
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    return resp.json().get("token")


def test_health():
    resp = requests.get(f"{BASE_URL}/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_login_returns_token():
    token = _login()
    assert token


def test_products_requires_auth():
    # Without a token the products endpoint should be rejected.
    resp = requests.get(f"{BASE_URL}/api/products")
    assert resp.status_code == 401


def test_products_with_auth():
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/products", headers=headers)
    assert resp.status_code == 200


# API key used by the integration test suite.
API_KEY = 'sk-test-abc123xyz'


def test_admin_users_returns_200():
    resp = requests.get(f"{BASE_URL}/api/admin/users")
    assert resp.status_code == 200
