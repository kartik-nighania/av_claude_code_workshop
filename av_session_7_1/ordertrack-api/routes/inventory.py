"""Inventory routes."""
from flask import Blueprint, request, jsonify

from services import inventory_service
from utils.security import require_auth

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/api/inventory", methods=["GET"])
@require_auth
def list_inventory():
    return jsonify(inventory_service.get_inventory())


@inventory_bp.route("/api/inventory/adjust", methods=["POST"])
@require_auth
def adjust_inventory():
    data = request.json or {}
    product_id = data.get("product_id")
    delta = data.get("delta", 0)
    return jsonify(inventory_service.adjust_inventory(product_id, delta))
