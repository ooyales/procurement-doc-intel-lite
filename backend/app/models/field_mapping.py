import uuid
from datetime import datetime, timezone
from app.extensions import db


class FieldMapping(db.Model):
    __tablename__ = 'field_mappings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_name = db.Column(db.String(200), index=True)
    source_column_name = db.Column(db.String(200), nullable=False)
    target_field = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, default=1.0)
    times_confirmed = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    session_id = db.Column(db.String(100), default='__default__', index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'vendor_name': self.vendor_name,
            'source_column_name': self.source_column_name,
            'target_field': self.target_field,
            'confidence': self.confidence,
            'times_confirmed': self.times_confirmed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
