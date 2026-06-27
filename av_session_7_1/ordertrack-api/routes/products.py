"""Product routes."""
from flask import Blueprint, jsonify

from services import product_service
from utils.security import require_auth

products_bp = Blueprint("products", __name__)


@products_bp.route("/api/products", methods=["GET"])
@require_auth
def list_products():
    return jsonify(product_service.get_products())


@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
@require_auth
def get_product(product_id):
    product = product_service.get_product(product_id)
    if not product:
        return jsonify({"error": "not found"}), 404
    return jsonify(product)
