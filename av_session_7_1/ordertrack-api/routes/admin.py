"""Admin routes."""
from flask import Blueprint, jsonify

from services import customer_service
from services.auth_service import _USERS

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/admin/users", methods=["GET"])
def admin_users():
    return jsonify(_USERS)


@admin_bp.route("/api/admin/customers", methods=["GET"])
def admin_customers():
    return jsonify(customer_service.get_customers())


@admin_bp.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    customers = customer_service.get_customers()
    return jsonify({"customer_count": len(customers)})
