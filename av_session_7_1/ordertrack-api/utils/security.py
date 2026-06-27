"""Auth decorator used by protected routes."""
from functools import wraps

from flask import request, jsonify

from services.auth_service import verify_token


def require_auth(fn):
    """Reject requests without a valid Bearer token."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        token = header.replace("Bearer ", "", 1)
        claims = verify_token(token)
        if not claims:
            return jsonify({"error": "unauthorized"}), 401
        request.user = claims
        return fn(*args, **kwargs)

    return wrapper
