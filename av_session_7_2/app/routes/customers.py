"""CRUD endpoints for /api/customers."""
from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Customer

customers_bp = Blueprint("customers", __name__, url_prefix="/api/customers")


@customers_bp.get("")
def list_customers():
    customers = Customer.query.order_by(Customer.id).all()
    return jsonify([c.to_dict() for c in customers])


@customers_bp.get("/<int:customer_id>")
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())


@customers_bp.post("")
def create_customer():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("email"):
        return jsonify(error="name and email are required"), 400

    customer = Customer(name=data["name"], email=data["email"])
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201


@customers_bp.put("/<int:customer_id>")
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json(silent=True) or {}
    customer.name = data.get("name", customer.name)
    customer.email = data.get("email", customer.email)
    db.session.commit()
    return jsonify(customer.to_dict())


@customers_bp.delete("/<int:customer_id>")
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify(deleted=customer_id)
