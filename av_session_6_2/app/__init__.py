"""HealthTrack API — Flask application factory.

A module-level ``app`` instance is exported so ``flask run`` (with FLASK_APP=app)
discovers it directly.
"""
import os

from flask import Flask

from .extensions import db


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

    db_user = os.environ.get("DB_USER", "healthtrack_user")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_host = os.environ.get("DB_HOST", "db")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "healthtrack")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from . import models  # noqa: F401 — register models before create_all()
    from .routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()
