"""OrderTrack API — Flask application factory.

Backend layering: routes (blueprints) -> models (SQLAlchemy) -> Postgres,
with Redis used as a cache for order-status lookups.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, init_redis


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Dev-friendly: frontend (Vite) talks to the API cross-origin.
    CORS(app)

    db.init_app(app)
    init_redis(app)

    # Blueprints (auth + CRUD: /api/orders, /api/products, /api/customers + health).
    from .routes.health import health_bp
    from .routes.auth import auth_bp
    from .routes.customers import customers_bp
    from .routes.products import products_bp
    from .routes.orders import orders_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)

    with app.app_context():
        from . import models  # noqa: F401  (register models before create_all)

        db.create_all()
        from .seed import seed_data

        seed_data()

    @app.errorhandler(404)
    def not_found(_err):
        return jsonify(error="not found"), 404

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify(error=str(err.description)), 400

    return app
