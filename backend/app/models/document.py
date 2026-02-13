import uuid
from datetime import datetime, timezone
from app.extensions import db


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Source file
    original_filename = db.Column(db.String(500), nullable=False)
    file_format = db.Column(db.String(10), nullable=False)  # pdf, xlsx, docx, csv
    file_size_bytes = db.Column(db.Integer)
    file_hash = db.Column(db.String(64))  # SHA-256
    stored_path = db.Column(db.String(500))

    # Classification
    document_type = db.Column(db.String(50))  # vendor_quote, purchase_order, invoice, bom, etc.

    # Extracted metadata
    vendor_name = db.Column(db.String(200))
    document_number = db.Column(db.String(100))  # PO#, Invoice#, Quote#
    document_date = db.Column(db.String(20))
    contract_number = db.Column(db.String(100))
    task_order_number = db.Column(db.String(100))
    period_of_performance_start = db.Column(db.String(20))
    period_of_performance_end = db.Column(db.String(20))
    total_amount = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')

    # Processing
    processing_status = db.Column(db.String(20), default='uploaded')
    # uploaded, extracting, mapping, review, complete, failed
    extraction_method = db.Column(db.String(50))  # pdfplumber, openpyxl, python-docx, pandas
    extraction_confidence = db.Column(db.Float)
    ai_model_used = db.Column(db.String(100))

    # Review
    reviewed_by = db.Column(db.String(200))
    reviewed_at = db.Column(db.String(30))
    review_notes = db.Column(db.Text)

    # RAG
    chunk_count = db.Column(db.Integer, default=0)
    embedded = db.Column(db.Integer, default=0)

    # Metadata
    uploaded_by = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    tags = db.Column(db.Text, default='[]')
    notes = db.Column(db.Text)
    session_id = db.Column(db.String(100), default='__default__', index=True)

    # Relationships
    line_items = db.relationship('LineItem', backref='document', lazy='dynamic',
                                 cascade='all, delete-orphan')
    chunks = db.relationship('DocumentChunk', backref='document', lazy='dynamic',
                             cascade='all, delete-orphan')

    def to_dict(self, include_items=False):
        d = {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_format': self.file_format,
            'file_size_bytes': self.file_size_bytes,
            'file_hash': self.file_hash,
            'stored_path': self.stored_path,
            'document_type': self.document_type,
            'vendor_name': self.vendor_name,
            'document_number': self.document_number,
            'document_date': self.document_date,
            'contract_number': self.contract_number,
            'task_order_number': self.task_order_number,
            'period_of_performance_start': self.period_of_performance_start,
            'period_of_performance_end': self.period_of_performance_end,
            'total_amount': self.total_amount,
            'currency': self.currency,
            'processing_status': self.processing_status,
            'extraction_method': self.extraction_method,
            'extraction_confidence': self.extraction_confidence,
            'ai_model_used': self.ai_model_used,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at,
            'review_notes': self.review_notes,
            'chunk_count': self.chunk_count,
            'embedded': self.embedded,
            'uploaded_by': self.uploaded_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags,
            'notes': self.notes,
            'line_item_count': self.line_items.count() if self.line_items else 0,
        }
        if include_items:
            d['line_items'] = [li.to_dict() for li in self.line_items.all()]
        return d
