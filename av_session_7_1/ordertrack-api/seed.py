"""Create tables and load sample data for the OrderTrack API.

Run once after the database is up:  python seed.py
"""
from sqlalchemy.orm import Session

from db import get_engine
from models import Base, Customer, Product, Inventory, Order
from services.auth_service import hash_password
from utils.logger import get_logger

log = get_logger("seed")


def seed():
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        customers = [
            Customer(name="Alice Johnson", email="alice@example.com",
                     password_hash=hash_password("alice123")),
            Customer(name="Bob Smith", email="bob@example.com",
                     password_hash=hash_password("bob123")),
            Customer(name="Carol White", email="carol@example.com",
                     password_hash=hash_password("carol123")),
        ]
        products = [
            Product(name="Mechanical Keyboard", price=89.99, sku="KB-001"),
            Product(name="Wireless Mouse", price=39.50, sku="MO-002"),
            Product(name="27in Monitor", price=249.00, sku="MON-003"),
            Product(name="USB-C Hub", price=29.99, sku="HUB-004"),
        ]
        s.add_all(customers + products)
        s.flush()

        s.add_all([
            Inventory(product_id=products[0].id, quantity=120, warehouse="main"),
            Inventory(product_id=products[1].id, quantity=300, warehouse="main"),
            Inventory(product_id=products[2].id, quantity=45, warehouse="main"),
            Inventory(product_id=products[3].id, quantity=0, warehouse="main"),
        ])
        s.add_all([
            Order(customer_id=customers[0].id, customer_name="Alice Johnson",
                  product_id=products[0].id, quantity=1, status="shipped"),
            Order(customer_id=customers[1].id, customer_name="Bob Smith",
                  product_id=products[1].id, quantity=2, status="pending"),
            Order(customer_id=customers[0].id, customer_name="Alice Johnson",
                  product_id=products[2].id, quantity=1, status="delivered"),
        ])
        s.commit()

    log.info("Seed complete: %d customers, %d products", len(customers), len(products))


if __name__ == "__main__":
    seed()
