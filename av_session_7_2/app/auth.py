"""JWT authentication: register/login endpoints, password hashing, and the
`require_auth` decorator used to protect routes.

Security notes:
- Passwords are hashed with bcrypt; the plaintext is never stored or logged.
- Tokens are HS256-signed with the app SECRET_KEY and expire after 24 hours.
"""

from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
from flask import Blueprint, current_app, g, jsonify, request

from .extensions import db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

TOKEN_TTL_HOURS = 24


# ---- password helpers -----------------------------------------------------
def hash_password(plain):
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain, hashed):
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---- token helpers --------------------------------------------------------
def make_token(user):
    now = datetime.utcnow()
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def require_auth(fn):
    """Reject requests without a valid, unexpired Bearer token (401)."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify(error="authorization required"), 401
        try:
            payload = jwt.decode(
                parts[1],
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return jsonify(error="token expired"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="invalid token"), 401

        g.user_id = payload.get("sub")
        g.user_email = payload.get("email")
        return fn(*args, **kwargs)

    return wrapper


# ---- endpoints ------------------------------------------------------------
@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    if not email or not password:
        return jsonify(error="email and password are required"), 400
    if User.query.filter_by(email=email).first() is not None:
        return jsonify(error="email already registered"), 409

    user = User(
        name=name or email,
        email=email,
        hashed_password=hash_password(password),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(token=make_token(user), user=user.to_dict()), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if user is None or not verify_password(password, user.hashed_password):
        # Same message either way — don't reveal which emails exist.
        return jsonify(error="invalid credentials"), 401
    return jsonify(token=make_token(user), user=user.to_dict())
