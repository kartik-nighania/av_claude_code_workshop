"""Data model for HealthTrack — a single health metric reading."""
from datetime import datetime, timezone

from .extensions import db


class Metric(db.Model):
    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)
    # e.g. "steps", "weight", "heart_rate", "sleep_hours"
    type = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    # e.g. "count", "kg", "bpm", "hours"
    unit = db.Column(db.String(20))
    recorded_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value,
            "unit": self.unit,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }
