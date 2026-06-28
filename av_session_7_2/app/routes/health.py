"""Health check — verifies Postgres and Redis are reachable."""
from flask import Blueprint, jsonify
from sqlalchemy import text

from ..extensions import db, get_redis

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    status = {"status": "ok", "db": "ok", "redis": "ok"}
    code = 200

    try:
        db.session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        status["db"] = f"error: {exc.__class__.__name__}"
        status["status"] = "degraded"
        code = 503

    try:
        cache = get_redis()
        if cache is None or not cache.ping():
            raise RuntimeError("no ping")
    except Exception as exc:  # noqa: BLE001
        status["redis"] = f"error: {exc.__class__.__name__}"
        status["status"] = "degraded"
        code = 503

    return jsonify(status), code
