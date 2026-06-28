"""JWT auth helpers: password hashing (bcrypt), token issue/verify, and the
`@require_auth` decorator for protecting routes.

Security notes:
- Passwords are hashed with bcrypt; plaintext is never stored or logged.
- Tokens are HS256-signed with the app SECRET_KEY and expire after 24 hours.
"""

from datetime import datetime, timedelta
from functools import wraps

import bcrypt
import jwt
from flask import current_app, g, jsonify, request

TOKEN_TTL = timedelta(hours=24)
_ALGORITHM = "HS256"


def hash_password(plaintext):
    """Return a bcrypt hash (str) for a plaintext password."""
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plaintext, hashed):
    """Constant-time check of a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def generate_token(user):
    """Issue a signed JWT carrying the user id + email, expiring in 24h."""
    now = datetime.utcnow()
    payload = {
        "sub": user.id,
        "email": user.email,
        "iat": now,
        "exp": now + TOKEN_TTL,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm=_ALGORITHM)


def decode_token(token):
    """Decode/validate a JWT, returning its payload (raises on invalid/expired)."""
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=[_ALGORITHM])


def require_auth(fn):
    """Reject requests without a valid `Authorization: Bearer <token>` header.

    On success, stashes the caller on `flask.g` (`g.user_id`, `g.user_email`).
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="missing or malformed Authorization header"), 401

        token = header[len("Bearer ") :].strip()
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify(error="token expired"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="invalid token"), 401

        g.user_id = payload.get("sub")
        g.user_email = payload.get("email")
        return fn(*args, **kwargs)

    return wrapper
