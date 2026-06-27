"""Order routes."""
from flask import Blueprint, request, jsonify

from services import order_service
from utils.logger import get_logger

orders_bp = Blueprint("orders", __name__)
log = get_logger("orders")


@orders_bp.route("/api/orders", methods=["GET"])
def list_orders():
    customer_id = request.args.get("customer_id")
    orders = order_service.get_orders(customer_id)
    return jsonify(orders)


@orders_bp.route("/api/orders/search", methods=["GET"])
def search_orders():
    customer_name = request.args.get("customer_name", "")
    rows = order_service.search_orders(customer_name)
    return jsonify([list(r) for r in rows])


@orders_bp.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = order_service.get_order(order_id)
    if not order:
        return jsonify({"error": "not found"}), 404
    return jsonify(order)


@orders_bp.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    customer_name = data["customer_name"]
    product_id = data["product_id"]
    quantity = data["quantity"]

    new_id = order_service.create_order(customer_name, product_id, quantity)
    log.info(f"Created order {new_id} for {customer_name}")
    return jsonify({"id": new_id}), 201
