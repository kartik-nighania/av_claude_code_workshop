"""Auth flow: register, login, and token validation on protected routes."""


def test_register_returns_token_and_user(client):
    resp = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["access_token"]
    assert body["user"]["email"] == "new@example.com"
    # The password hash must never be exposed.
    assert "hashed_password" not in body["user"]
    assert "password" not in body["user"]


def test_register_missing_fields_400(client):
    resp = client.post("/auth/register", json={"email": "x@example.com"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_register_duplicate_email_409(client):
    payload = {"email": "dup@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_success(client, user):
    resp = client.post(
        "/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert resp.status_code == 200
    assert resp.get_json()["access_token"]


def test_login_wrong_password_401(client, user):
    resp = client.post(
        "/auth/login",
        json={"email": user["email"], "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_login_unknown_user_401(client):
    resp = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/api/products")
    assert resp.status_code == 401


def test_protected_route_with_valid_token(client, auth_headers):
    resp = client.get("/api/products", headers=auth_headers)
    assert resp.status_code == 200


def test_malformed_authorization_header_401(client):
    resp = client.get("/api/products", headers={"Authorization": "Token abc"})
    assert resp.status_code == 401


def test_invalid_token_401(client):
    resp = client.get(
        "/api/products",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "invalid token"


def test_expired_token_401(client, expired_token):
    resp = client.get(
        "/api/products",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "token expired"
