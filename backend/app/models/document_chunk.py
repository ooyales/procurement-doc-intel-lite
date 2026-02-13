import uuid
from datetime import datetime, timezone
from app.extensions import db


class DocumentChunk(db.Model):
    __tablename__ = 'document_chunks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False, index=True)
    chunk_index = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=False)
    chunk_type = db.Column(db.String(30))  # header, table, paragraph, terms, metadata
    page_number = db.Column(db.Integer)

    # Embedding stored as JSON text (or NULL if using external store)
    embedding = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    session_id = db.Column(db.String(100), default='__default__', index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'chunk_index': self.chunk_index,
            'content': self.content,
            'chunk_type': self.chunk_type,
            'page_number': self.page_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
