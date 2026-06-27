"""Authentication routes."""
from flask import Blueprint, request, jsonify

from services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    token = auth_service.login(username, password)
    if not token:
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"token": token})
