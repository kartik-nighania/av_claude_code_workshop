"""CRUD endpoints for /api/products."""
from flask import Blueprint, jsonify, request

from ..auth import require_auth
from ..extensions import db
from ..models import Product

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.get("")
@require_auth
def list_products():
    products = Product.query.order_by(Product.id).all()
    return jsonify([p.to_dict() for p in products])


@products_bp.get("/<int:product_id>")
@require_auth
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@products_bp.post("")
@require_auth
def create_product():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("sku"):
        return jsonify(error="name and sku are required"), 400

    product = Product(
        name=data["name"],
        sku=data["sku"],
        price=data.get("price", 0),
        stock=data.get("stock", 0),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@products_bp.put("/<int:product_id>")
@require_auth
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(silent=True) or {}
    product.name = data.get("name", product.name)
    product.sku = data.get("sku", product.sku)
    product.price = data.get("price", product.price)
    product.stock = data.get("stock", product.stock)
    db.session.commit()
    return jsonify(product.to_dict())


@products_bp.delete("/<int:product_id>")
@require_auth
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify(deleted=product_id)
