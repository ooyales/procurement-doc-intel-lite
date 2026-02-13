import hashlib
import os
import uuid
import logging
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.extensions import db
from app.models.document import Document
from app.models.line_item import LineItem
from app.models.document_chunk import DocumentChunk
from app.models.field_mapping import FieldMapping
from app.errors import BadRequestError, NotFoundError

logger = logging.getLogger(__name__)

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'docx', 'doc', 'csv'}


def _get_extension(filename):
    """Extract and return lowercase file extension."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


@documents_bp.route('', methods=['GET'])
@jwt_required()
def list_documents():
    """List documents with filters and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)

    query = Document.query.filter_by(session_id='__default__')

    # Filters
    document_type = request.args.get('document_type')
    if document_type:
        query = query.filter(Document.document_type == document_type)

    vendor_name = request.args.get('vendor_name')
    if vendor_name:
        query = query.filter(Document.vendor_name.ilike(f'%{vendor_name}%'))

    processing_status = request.args.get('processing_status')
    if processing_status:
        query = query.filter(Document.processing_status == processing_status)

    search = request.args.get('search', '').strip()
    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            db.or_(
                Document.original_filename.ilike(search_filter),
                Document.vendor_name.ilike(search_filter),
                Document.document_number.ilike(search_filter),
                Document.contract_number.ilike(search_filter),
            )
        )

    # Order and paginate
    query = query.order_by(Document.created_at.desc())
    total = query.count()
    documents = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'items': [doc.to_dict() for doc in documents],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@documents_bp.route('/<doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    """Get single document with line items."""
    doc = Document.query.get(doc_id)
    if not doc:
        raise NotFoundError(f'Document {doc_id} not found')
    return jsonify(doc.to_dict(include_items=True))


@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a document file."""
    if 'file' not in request.files:
        raise BadRequestError('No file provided')

    file = request.files['file']
    if not file.filename:
        raise BadRequestError('No filename provided')

    ext = _get_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestError(
            f'Unsupported file format: {ext}. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
        )

    # Read file content for hashing
    file_content = file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    file.seek(0)

    # Generate unique stored filename
    stored_filename = f'{uuid.uuid4().hex}_{file.filename}'
    upload_folder = current_app.config.get('UPLOAD_FOLDER', '/app/uploads')
    os.makedirs(upload_folder, exist_ok=True)
    stored_path = os.path.join(upload_folder, stored_filename)

    file.save(stored_path)

    # Determine file format
    file_format = ext
    if file_format == 'xls':
        file_format = 'xlsx'
    if file_format == 'doc':
        file_format = 'docx'

    # Get uploader identity
    identity = get_jwt_identity()

    doc = Document(
        original_filename=file.filename,
        file_format=file_format,
        file_size_bytes=len(file_content),
        file_hash=file_hash,
        stored_path=stored_path,
        processing_status='uploaded',
        uploaded_by=identity,
        session_id='__default__',
    )

    db.session.add(doc)
    db.session.commit()

    return jsonify(doc.to_dict()), 201


@documents_bp.route('/<doc_id>/process', methods=['POST'])
@jwt_required()
def process_document(doc_id):
    """Trigger extraction and AI mapping pipeline for a document."""
    doc = Document.query.get(doc_id)
    if not doc:
        raise NotFoundError(f'Document {doc_id} not found')

    api_key = current_app.config.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        raise BadRequestError('ANTHROPIC_API_KEY is not configured. Set it in environment variables.')

    try:
        # Stage 1: Extraction
        doc.processing_status = 'extracting'
        db.session.commit()

        from app.services.extractor import DocumentExtractor
        extractor = DocumentExtractor()
        extraction = extractor.extract(doc.stored_path, doc.file_format)

        doc.extraction_method = extraction.get('method', 'unknown')

        # Stage 2: AI Field Mapping
        doc.processing_status = 'mapping'
        db.session.commit()

        from app.services.field_mapper import FieldMapper
        mapper = FieldMapper(api_key)

        # Load known mappings for this vendor
        known_mappings = {}
        if doc.vendor_name:
            existing = FieldMapping.query.filter_by(
                vendor_name=doc.vendor_name,
                session_id='__default__',
            ).all()
            known_mappings = {fm.source_column_name: fm.target_field for fm in existing}

        result = mapper.map_document(
            raw_tables=extraction.get('tables', []),
            document_text=extraction.get('full_text', ''),
            file_format=doc.file_format,
            known_mappings=known_mappings,
        )

        # Check for mapping errors
        if result.get('error'):
            logger.warning(f'Mapping returned error for doc {doc_id}: {result["error"]}')

        # Update document metadata from AI results
        metadata = result.get('metadata', {})
        doc.document_type = result.get('document_type', doc.document_type)
        doc.vendor_name = metadata.get('vendor_name') or doc.vendor_name
        doc.document_number = metadata.get('document_number') or doc.document_number
        doc.document_date = metadata.get('document_date') or doc.document_date
        doc.contract_number = metadata.get('contract_number') or doc.contract_number
        doc.task_order_number = metadata.get('task_order_number') or doc.task_order_number
        doc.total_amount = metadata.get('total_amount') or doc.total_amount
        doc.period_of_performance_start = metadata.get('period_of_performance_start') or doc.period_of_performance_start
        doc.period_of_performance_end = metadata.get('period_of_performance_end') or doc.period_of_performance_end
        doc.ai_model_used = 'claude-sonnet-4-5-20250929'

        # Create line items
        line_items_data = result.get('line_items', [])
        for li_data in line_items_data:
            li = LineItem(
                document_id=doc.id,
                line_number=li_data.get('line_number'),
                clin=li_data.get('clin'),
                part_number=li_data.get('part_number'),
                manufacturer=li_data.get('manufacturer'),
                product_name=li_data.get('product_name'),
                product_description=li_data.get('product_description'),
                category=li_data.get('category'),
                sub_category=li_data.get('sub_category'),
                quantity=_safe_float(li_data.get('quantity')),
                unit_of_issue=li_data.get('unit_of_issue'),
                unit_price=_safe_float(li_data.get('unit_price')),
                extended_price=_safe_float(li_data.get('extended_price')),
                labor_category=li_data.get('labor_category'),
                labor_hours=_safe_float(li_data.get('labor_hours')),
                labor_rate=_safe_float(li_data.get('labor_rate')),
                mapping_confidence=_safe_float(li_data.get('mapping_confidence')),
                original_row_text=str(li_data),
                session_id='__default__',
            )
            db.session.add(li)

        # Create document chunks for RAG
        full_text = extraction.get('full_text', '')
        if full_text:
            chunks = _create_chunks(full_text)
            for idx, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    content=chunk_text,
                    chunk_type='paragraph',
                    session_id='__default__',
                )
                db.session.add(chunk)
            doc.chunk_count = len(chunks)

        # Calculate extraction confidence as average of line item confidences
        confidences = [
            li_data.get('mapping_confidence', 0)
            for li_data in line_items_data
            if li_data.get('mapping_confidence') is not None
        ]
        if confidences:
            doc.extraction_confidence = round(sum(confidences) / len(confidences), 3)

        doc.processing_status = 'review'
        db.session.commit()

        return jsonify({
            'message': 'Document processed successfully',
            'document': doc.to_dict(include_items=True),
            'line_items_created': len(line_items_data),
            'chunks_created': doc.chunk_count or 0,
        })

    except Exception as e:
        logger.exception(f'Processing failed for document {doc_id}')
        doc.processing_status = 'failed'
        doc.notes = f'Processing error: {str(e)}'
        db.session.commit()
        raise BadRequestError(f'Processing failed: {str(e)}')


@documents_bp.route('/<doc_id>', methods=['PUT'])
@jwt_required()
def update_document(doc_id):
    """Update document metadata fields."""
    doc = Document.query.get(doc_id)
    if not doc:
        raise NotFoundError(f'Document {doc_id} not found')

    data = request.get_json()
    if not data:
        raise BadRequestError('Request body is required')

    updatable_fields = [
        'document_type', 'vendor_name', 'document_number', 'document_date',
        'contract_number', 'task_order_number', 'period_of_performance_start',
        'period_of_performance_end', 'total_amount', 'currency', 'tags',
        'notes', 'review_notes',
    ]

    for field in updatable_fields:
        if field in data:
            setattr(doc, field, data[field])

    db.session.commit()
    return jsonify(doc.to_dict())


@documents_bp.route('/<doc_id>/approve', methods=['PUT'])
@jwt_required()
def approve_document(doc_id):
    """Mark document as reviewed/complete."""
    doc = Document.query.get(doc_id)
    if not doc:
        raise NotFoundError(f'Document {doc_id} not found')

    identity = get_jwt_identity()
    claims = get_jwt()

    doc.processing_status = 'complete'
    doc.reviewed_by = claims.get('display_name', identity)
    doc.reviewed_at = datetime.now(timezone.utc).isoformat()

    # Allow optional review notes
    data = request.get_json(silent=True)
    if data and data.get('review_notes'):
        doc.review_notes = data['review_notes']

    db.session.commit()
    return jsonify(doc.to_dict())


@documents_bp.route('/<doc_id>/reprocess', methods=['PUT'])
@jwt_required()
def reprocess_document(doc_id):
    """Reset document to uploaded state and clear existing extracted data."""
    doc = Document.query.get(doc_id)
    if not doc:
        raise NotFoundError(f'Document {doc_id} not found')

    # Delete existing line items
    LineItem.query.filter_by(document_id=doc.id).delete()
    # Delete existing chunks
    DocumentChunk.query.filter_by(document_id=doc.id).delete()

    # Reset processing fields
    doc.processing_status = 'uploaded'
    doc.extraction_method = None
    doc.extraction_confidence = None
    doc.ai_model_used = None
    doc.chunk_count = 0
    doc.reviewed_by = None
    doc.reviewed_at = None
    doc.review_notes = None

    db.session.commit()

    return jsonify({
        'message': 'Document reset for reprocessing',
        'document': doc.to_dict(),
    })


@documents_bp.route('/<doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    """Delete document and all related records."""
    doc = Document.query.get(doc_id)
    if not doc:
        raise NotFoundError(f'Document {doc_id} not found')

    # Delete stored file
    if doc.stored_path and os.path.exists(doc.stored_path):
        try:
            os.remove(doc.stored_path)
        except OSError:
            logger.warning(f'Could not delete file: {doc.stored_path}')

    # Delete related records (cascade handles line_items and chunks)
    db.session.delete(doc)
    db.session.commit()

    return jsonify({'message': f'Document {doc_id} deleted'})


def _safe_float(value):
    """Safely convert a value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _create_chunks(text, chunk_size=800, overlap=100):
    """Split text into overlapping chunks for RAG."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
        if start >= len(text):
            break
    return chunks
