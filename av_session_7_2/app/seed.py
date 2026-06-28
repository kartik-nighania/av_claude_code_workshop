"""Seed a few rows so the app shows data on first run (idempotent)."""
from .extensions import db
from .models import Customer, Product, Order, OrderItem


def seed_data():
    if Customer.query.first() is not None:
        return

    alice = Customer(name="Alice Smith", email="alice@example.com")
    bob = Customer(name="Bob Jones", email="bob@example.com")
    db.session.add_all([alice, bob])

    widget = Product(name="Widget", sku="WGT-001", price=9.99, stock=100)
    gadget = Product(name="Gadget", sku="GDG-002", price=24.50, stock=40)
    gizmo = Product(name="Gizmo", sku="GZM-003", price=4.25, stock=250)
    db.session.add_all([widget, gadget, gizmo])
    db.session.flush()  # assign ids before referencing them

    order = Order(customer_id=alice.id, status="paid")
    order.items = [
        OrderItem(product_id=widget.id, quantity=2, unit_price=widget.price),
        OrderItem(product_id=gizmo.id, quantity=5, unit_price=gizmo.price),
    ]
    db.session.add(order)

    db.session.commit()
