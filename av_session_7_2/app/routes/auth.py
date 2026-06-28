"""Auth endpoints: register + login, issuing 24h JWT access tokens."""
from flask import Blueprint, jsonify, request

from ..auth import generate_token, hash_password, verify_password
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify(error="email and password are required"), 400

    if User.query.filter_by(email=email).first() is not None:
        return jsonify(error="email already registered"), 409

    user = User(email=email, hashed_password=hash_password(password))
    db.session.add(user)
    db.session.commit()

    token = generate_token(user)
    return jsonify(user=user.to_dict(), access_token=token), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    # Same response whether the email is unknown or the password is wrong.
    if user is None or not verify_password(password, user.hashed_password):
        return jsonify(error="invalid credentials"), 401

    token = generate_token(user)
    return jsonify(user=user.to_dict(), access_token=token)
