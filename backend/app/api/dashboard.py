from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.document import Document
from app.models.line_item import LineItem
from app.models.canonical_product import CanonicalProduct

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Return dashboard KPIs and summary data."""
    session_filter = '__default__'

    # Total documents
    total_documents = Document.query.filter_by(session_id=session_filter).count()

    # Documents by status
    status_rows = db.session.query(
        Document.processing_status,
        db.func.count(Document.id),
    ).filter_by(session_id=session_filter)\
     .group_by(Document.processing_status)\
     .all()
    documents_by_status = {row[0]: row[1] for row in status_rows if row[0]}

    # Documents by type
    type_rows = db.session.query(
        Document.document_type,
        db.func.count(Document.id),
    ).filter_by(session_id=session_filter)\
     .filter(Document.document_type.isnot(None))\
     .group_by(Document.document_type)\
     .all()
    documents_by_type = {row[0]: row[1] for row in type_rows if row[0]}

    # Total line items
    total_line_items = LineItem.query.filter_by(session_id=session_filter).count()

    # Total canonical products
    total_products = CanonicalProduct.query.filter_by(session_id=session_filter).count()

    # Total spend (sum of extended_price)
    total_spend_result = db.session.query(
        db.func.sum(LineItem.extended_price),
    ).filter_by(session_id=session_filter).scalar()
    total_spend = round(total_spend_result or 0, 2)

    # Top vendors by document count and spend
    top_vendors_rows = db.session.query(
        Document.vendor_name,
        db.func.count(db.distinct(Document.id)).label('doc_count'),
        db.func.sum(LineItem.extended_price).label('total_spend'),
    ).join(LineItem, LineItem.document_id == Document.id)\
     .filter(Document.session_id == session_filter)\
     .filter(Document.vendor_name.isnot(None))\
     .group_by(Document.vendor_name)\
     .order_by(db.func.sum(LineItem.extended_price).desc())\
     .limit(10)\
     .all()

    top_vendors = [
        {
            'vendor_name': row[0],
            'document_count': row[1],
            'total_spend': round(row[2] or 0, 2),
        }
        for row in top_vendors_rows
    ]

    # Spend by category
    category_rows = db.session.query(
        LineItem.category,
        db.func.sum(LineItem.extended_price),
    ).filter_by(session_id=session_filter)\
     .filter(LineItem.category.isnot(None))\
     .group_by(LineItem.category)\
     .order_by(db.func.sum(LineItem.extended_price).desc())\
     .all()

    spend_by_category = [
        {'category': row[0], 'total': round(row[1] or 0, 2)}
        for row in category_rows
    ]

    # Recent documents (last 10)
    recent_docs = Document.query.filter_by(session_id=session_filter)\
        .order_by(Document.created_at.desc())\
        .limit(10)\
        .all()

    # Processing queue (not complete, ordered by created_at)
    processing_queue = Document.query.filter_by(session_id=session_filter)\
        .filter(Document.processing_status != 'complete')\
        .order_by(Document.created_at.asc())\
        .all()

    return jsonify({
        'total_documents': total_documents,
        'documents_by_status': documents_by_status,
        'documents_by_type': documents_by_type,
        'total_line_items': total_line_items,
        'total_products': total_products,
        'total_spend': total_spend,
        'top_vendors': top_vendors,
        'spend_by_category': spend_by_category,
        'recent_documents': [doc.to_dict() for doc in recent_docs],
        'processing_queue': [doc.to_dict() for doc in processing_queue],
    })
