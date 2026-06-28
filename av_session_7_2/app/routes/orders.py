"""CRUD endpoints for /api/orders, plus a cached status lookup."""
from flask import Blueprint, jsonify, request

from ..auth import require_auth
from ..extensions import db
from ..models import ORDER_STATUSES, Order, OrderItem, Product
from ..order_status import get_order_status, invalidate_order_status

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.get("")
@require_auth
def list_orders():
    orders = Order.query.order_by(Order.id).all()
    return jsonify([o.to_dict() for o in orders])


@orders_bp.get("/<int:order_id>")
@require_auth
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())


@orders_bp.get("/<int:order_id>/status")
@require_auth
def order_status(order_id):
    status = get_order_status(order_id)
    if status is None:
        return jsonify(error="not found"), 404
    return jsonify(status)


@orders_bp.post("")
@require_auth
def create_order():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")
    items = data.get("items", [])
    if not customer_id or not items:
        return jsonify(error="customer_id and at least one item are required"), 400

    order = Order(customer_id=customer_id, status=data.get("status", "pending"))
    for item in items:
        product = Product.query.get(item.get("product_id"))
        if product is None:
            return jsonify(error=f"product {item.get('product_id')} not found"), 400
        order.items.append(
            OrderItem(
                product_id=product.id,
                quantity=item.get("quantity", 1),
                unit_price=product.price,
            )
        )

    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@orders_bp.put("/<int:order_id>")
@require_auth
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json(silent=True) or {}

    new_status = data.get("status")
    if new_status is not None:
        if new_status not in ORDER_STATUSES:
            return jsonify(error=f"status must be one of {ORDER_STATUSES}"), 400
        order.status = new_status

    db.session.commit()
    invalidate_order_status(order_id)  # status may have changed
    return jsonify(order.to_dict())


@orders_bp.delete("/<int:order_id>")
@require_auth
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    invalidate_order_status(order_id)
    return jsonify(deleted=order_id)
