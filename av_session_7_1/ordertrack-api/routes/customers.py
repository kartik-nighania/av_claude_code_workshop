"""Customer routes."""
from flask import Blueprint, jsonify

from services import customer_service
from utils.security import require_auth

customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/api/customers", methods=["GET"])
@require_auth
def list_customers():
    return jsonify(customer_service.get_customers())


@customers_bp.route("/api/customers/<int:customer_id>", methods=["GET"])
@require_auth
def get_customer(customer_id):
    customer = customer_service.get_customer(customer_id)
    if not customer:
        return jsonify({"error": "not found"}), 404
    return jsonify(customer)
