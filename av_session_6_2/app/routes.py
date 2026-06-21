"""HTTP routes for the HealthTrack API.

The /health route follows the design from the deployment spec: it pings every
backing dependency (Postgres + Redis) and returns 503 if any one is degraded so
a load balancer can pull the instance out of rotation.
"""
import json

from flask import Blueprint, jsonify, request
from sqlalchemy import text

from .extensions import cache, db
from .models import Metric

bp = Blueprint("api", __name__)

METRICS_CACHE_KEY = "metrics:list"
CACHE_TTL_SECONDS = 30


@bp.route("/")
def index():
    return jsonify(
        {
            "service": "HealthTrack API",
            "description": "Log and retrieve personal health metrics.",
            "endpoints": {
                "GET /health": "Liveness + dependency (DB, cache) check",
                "GET /metrics": "List recorded metrics (Redis-cached)",
                "POST /metrics": "Record a metric {type, value, unit?}",
                "GET /metrics/<id>": "Fetch a single metric",
            },
        }
    )


@bp.route("/health")
def health_check():
    checks = {}

    # DB ping
    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:  # noqa: BLE001 — surface the failure string to the caller
        checks["database"] = str(e)

    # Redis ping
    try:
        cache.ping()
        checks["cache"] = "ok"
    except Exception as e:  # noqa: BLE001
        checks["cache"] = str(e)

    status = 200 if all(v == "ok" for v in checks.values()) else 503
    return jsonify({"status": "ok", "checks": checks}), status


@bp.route("/metrics", methods=["POST"])
def create_metric():
    data = request.get_json(silent=True) or {}
    if "type" not in data or "value" not in data:
        return jsonify({"error": "fields 'type' and 'value' are required"}), 400
    try:
        value = float(data["value"])
    except (TypeError, ValueError):
        return jsonify({"error": "'value' must be a number"}), 400

    metric = Metric(type=str(data["type"]), value=value, unit=data.get("unit"))
    db.session.add(metric)
    db.session.commit()

    # Invalidate the cached list so the next GET reflects this write.
    try:
        cache.delete(METRICS_CACHE_KEY)
    except Exception:  # noqa: BLE001 — cache miss is non-fatal
        pass

    return jsonify(metric.to_dict()), 201


@bp.route("/metrics", methods=["GET"])
def list_metrics():
    # Serve from cache when warm.
    try:
        cached = cache.get(METRICS_CACHE_KEY)
        if cached:
            return jsonify({"source": "cache", "metrics": json.loads(cached)})
    except Exception:  # noqa: BLE001 — cache down: fall back to the DB
        pass

    metrics = [
        m.to_dict() for m in Metric.query.order_by(Metric.recorded_at.desc()).all()
    ]

    try:
        cache.setex(METRICS_CACHE_KEY, CACHE_TTL_SECONDS, json.dumps(metrics))
    except Exception:  # noqa: BLE001
        pass

    return jsonify({"source": "database", "metrics": metrics})


@bp.route("/metrics/<int:metric_id>", methods=["GET"])
def get_metric(metric_id):
    metric = db.session.get(Metric, metric_id)
    if metric is None:
        return jsonify({"error": "metric not found"}), 404
    return jsonify(metric.to_dict())
