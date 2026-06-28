"""Auth: register, login, token validation (expiry / invalid / missing)."""


def test_register_creates_user(client):
    resp = client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@new.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["token"]
    assert body["user"]["email"] == "alice@new.com"
    assert body["user"]["name"] == "Alice"
    # The hash must never be exposed.
    assert "hashed_password" not in body["user"]
    assert "password" not in body["user"]


def test_register_defaults_name_to_email(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "noname@new.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    assert resp.get_json()["user"]["name"] == "noname@new.com"


def test_register_missing_fields_400(client):
    resp = client.post("/api/auth/register", json={"email": "x@y.com"})
    assert resp.status_code == 400


def test_register_duplicate_email_409(client, user):
    resp = client.post(
        "/api/auth/register",
        json={"email": user["email"], "password": "whatever"},
    )
    assert resp.status_code == 409


def test_login_success(client, user):
    resp = client.post(
        "/api/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert resp.status_code == 200
    assert resp.get_json()["token"]


def test_login_wrong_password_401(client, user):
    resp = client.post(
        "/api/auth/login",
        json={"email": user["email"], "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_unknown_email_401(client):
    resp = client.post(
        "/api/auth/login",
        json={"email": "ghost@nowhere.com", "password": "x"},
    )
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    assert client.get("/api/orders").status_code == 401


def test_invalid_token_401(client):
    resp = client.get(
        "/api/orders", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp.status_code == 401


def test_malformed_auth_header_401(client):
    resp = client.get("/api/orders", headers={"Authorization": "Token abc"})
    assert resp.status_code == 401


def test_expired_token_401(client, expired_headers):
    resp = client.get("/api/orders", headers=expired_headers)
    assert resp.status_code == 401


def test_valid_token_allows_access(client, auth_headers):
    assert client.get("/api/orders", headers=auth_headers).status_code == 200
