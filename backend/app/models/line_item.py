import uuid
from datetime import datetime, timezone
from app.extensions import db


class LineItem(db.Model):
    __tablename__ = 'line_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False, index=True)

    # Line identification
    line_number = db.Column(db.Integer)
    clin = db.Column(db.String(50))
    slin = db.Column(db.String(50))

    # Product identification
    part_number = db.Column(db.String(100), index=True)
    manufacturer = db.Column(db.String(200))
    manufacturer_part_number = db.Column(db.String(100))
    product_name = db.Column(db.String(500), index=True)
    product_description = db.Column(db.Text)

    # Categorization
    category = db.Column(db.String(50), index=True)
    # hardware, software, service, license, maintenance, labor, other
    sub_category = db.Column(db.String(100))

    # Quantity and pricing
    quantity = db.Column(db.Float)
    unit_of_issue = db.Column(db.String(50))  # each, lot, month, year, hour
    unit_price = db.Column(db.Float)
    extended_price = db.Column(db.Float)
    discount_percent = db.Column(db.Float)
    discount_amount = db.Column(db.Float)

    # For labor items
    labor_category = db.Column(db.String(200))
    labor_hours = db.Column(db.Float)
    labor_rate = db.Column(db.Float)

    # Period
    period_start = db.Column(db.String(20))
    period_end = db.Column(db.String(20))

    # Mapping confidence
    mapping_confidence = db.Column(db.Float)
    human_verified = db.Column(db.Integer, default=0)

    # Original text
    original_row_text = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    session_id = db.Column(db.String(100), default='__default__', index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'line_number': self.line_number,
            'clin': self.clin,
            'slin': self.slin,
            'part_number': self.part_number,
            'manufacturer': self.manufacturer,
            'manufacturer_part_number': self.manufacturer_part_number,
            'product_name': self.product_name,
            'product_description': self.product_description,
            'category': self.category,
            'sub_category': self.sub_category,
            'quantity': self.quantity,
            'unit_of_issue': self.unit_of_issue,
            'unit_price': self.unit_price,
            'extended_price': self.extended_price,
            'discount_percent': self.discount_percent,
            'discount_amount': self.discount_amount,
            'labor_category': self.labor_category,
            'labor_hours': self.labor_hours,
            'labor_rate': self.labor_rate,
            'period_start': self.period_start,
            'period_end': self.period_end,
            'mapping_confidence': self.mapping_confidence,
            'human_verified': self.human_verified,
            'original_row_text': self.original_row_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'vendor_name': self.document.vendor_name if self.document else None,
            'document_number': self.document.document_number if self.document else None,
            'document_type': self.document.document_type if self.document else None,
            'document_date': self.document.document_date if self.document else None,
            'original_filename': self.document.original_filename if self.document else None,
        }
