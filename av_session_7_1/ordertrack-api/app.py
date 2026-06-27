"""OrderTrack API — Flask application entry point.

Python 3.11 · Flask · PostgreSQL · Redis

Endpoints: Orders, Products, Customers, Inventory (+ Auth, Admin).
"""
import os

import redis
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

import config
from utils.logger import get_logger

log = get_logger("app")


def create_app():
    app = Flask(__name__)
    # Load configuration from config.py.
    app.config.from_object("config")

    # Redis client used for caching / session storage.
    app.redis = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        db=0,
    )

    from routes.orders import orders_bp
    from routes.products import products_bp
    from routes.customers import customers_bp
    from routes.inventory import inventory_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.reviews import reviews_bp

    app.register_blueprint(orders_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reviews_bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "ordertrack-api"})

    @app.errorhandler(Exception)
    def handle_uncaught(err):
        # Let normal HTTP errors (404, 405, ...) through unchanged.
        if isinstance(err, HTTPException):
            return err
        # Anything else is an unexpected 500 — record the full traceback so it
        # shows up in logs/app.log, then return a clean JSON error.
        log.exception("Unhandled error on %s %s", request.method, request.path)
        return jsonify({"error": "internal server error"}), 500

    log.info("OrderTrack API initialised (DEBUG=%s)", app.config.get("DEBUG"))
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=config.DEBUG)
