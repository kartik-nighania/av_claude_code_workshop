"""SQLAlchemy ORM models for the OrderTrack API."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    password_hash = Column(String(64), nullable=False, default="")
    created_at = Column(DateTime, server_default=func.now())

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    sku = Column(String(64), nullable=False)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    warehouse = Column(String(64), nullable=False, default="main")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer_name = Column(String(120), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="orders")
