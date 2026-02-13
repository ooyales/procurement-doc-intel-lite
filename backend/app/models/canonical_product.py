import json
import uuid
from datetime import datetime, timezone
from app.extensions import db


class CanonicalProduct(db.Model):
    __tablename__ = 'canonical_products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    canonical_name = db.Column(db.String(300), nullable=False, index=True)
    category = db.Column(db.String(50))
    manufacturer = db.Column(db.String(200), index=True)

    # Known identifiers
    known_part_numbers = db.Column(db.Text, default='[]')  # JSON array
    known_aliases = db.Column(db.Text, default='[]')  # JSON array

    # Pricing intelligence
    last_known_price = db.Column(db.Float)
    last_price_date = db.Column(db.String(20))
    avg_price = db.Column(db.Float)
    min_price = db.Column(db.Float)
    max_price = db.Column(db.Float)
    price_history = db.Column(db.Text, default='[]')  # JSON array

    # Asset Tracker link
    asset_tracker_category = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    session_id = db.Column(db.String(100), default='__default__', index=True)

    def to_dict(self):
        def _parse_json(val):
            if not val:
                return []
            try:
                return json.loads(val)
            except (json.JSONDecodeError, TypeError):
                return []

        return {
            'id': self.id,
            'canonical_name': self.canonical_name,
            'category': self.category,
            'manufacturer': self.manufacturer,
            'known_part_numbers': _parse_json(self.known_part_numbers),
            'known_aliases': _parse_json(self.known_aliases),
            'last_known_price': self.last_known_price,
            'last_price_date': self.last_price_date,
            'avg_price': self.avg_price,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'price_history': _parse_json(self.price_history),
            'asset_tracker_category': self.asset_tracker_category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
