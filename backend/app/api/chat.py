import logging
import random

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.document import Document
from app.models.line_item import LineItem
from app.errors import BadRequestError

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat_bp.route('', methods=['POST'])
@jwt_required()
def chat():
    """Process a natural-language query about procurement data."""
    data = request.get_json()
    if not data or not data.get('message', '').strip():
        raise BadRequestError('Message is required')

    message = data['message'].strip()
    history = data.get('history', [])

    try:
        from app.services.chat_service import ChatService
        service = ChatService(db_session=db.session, session_id='__default__')
        result = service.answer(message=message, history=history)
        return jsonify({
            'answer': result.get('answer', ''),
            'sources': result.get('sources', []),
            'query_type': result.get('query_type', 'general'),
        })
    except ImportError:
        logger.warning('ChatService not available, returning fallback response')
        return jsonify({
            'answer': 'Chat service is not yet configured. Please ensure the chat_service module is installed.',
            'sources': [],
            'query_type': 'error',
        })
    except Exception as e:
        logger.exception('Chat service error')
        return jsonify({
            'answer': f'An error occurred while processing your question: {str(e)}',
            'sources': [],
            'query_type': 'error',
        }), 500


@chat_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def suggestions():
    """Return suggested queries based on what data exists in the database."""
    session_filter = '__default__'

    # Gather distinct vendors
    vendor_rows = db.session.query(Document.vendor_name)\
        .filter(Document.session_id == session_filter)\
        .filter(Document.vendor_name.isnot(None))\
        .distinct()\
        .limit(20)\
        .all()
    vendors = [r[0] for r in vendor_rows if r[0]]

    # Gather distinct product names
    product_rows = db.session.query(LineItem.product_name)\
        .filter(LineItem.session_id == session_filter)\
        .filter(LineItem.product_name.isnot(None))\
        .distinct()\
        .limit(20)\
        .all()
    products = [r[0] for r in product_rows if r[0]]

    # Gather distinct categories
    category_rows = db.session.query(LineItem.category)\
        .filter(LineItem.session_id == session_filter)\
        .filter(LineItem.category.isnot(None))\
        .distinct()\
        .all()
    categories = [r[0] for r in category_rows if r[0]]

    # Gather distinct contract numbers
    contract_rows = db.session.query(Document.contract_number)\
        .filter(Document.session_id == session_filter)\
        .filter(Document.contract_number.isnot(None))\
        .distinct()\
        .limit(10)\
        .all()
    contracts = [r[0] for r in contract_rows if r[0]]

    # Build suggestion pool
    suggestion_pool = []

    # Generic suggestions always available
    suggestion_pool.extend([
        'What is our total spend across all documents?',
        'Which vendors have the highest total spend?',
        'Show me a breakdown of spend by category.',
    ])

    # Vendor-specific suggestions
    for vendor in vendors[:5]:
        suggestion_pool.append(f'What did we purchase from {vendor}?')
        suggestion_pool.append(f'How much did we spend with {vendor}?')

    # Product-specific suggestions
    for product in products[:5]:
        short_name = product[:60] if len(product) > 60 else product
        suggestion_pool.append(f'Show all line items for "{short_name}".')

    # Category suggestions
    for cat in categories[:3]:
        suggestion_pool.append(f'What is our total {cat} spend?')

    # Contract suggestions
    for contract in contracts[:3]:
        suggestion_pool.append(f'Show all items under contract {contract}.')

    # Price analysis suggestions
    if products:
        suggestion_pool.append('Which products have the highest unit prices?')
        suggestion_pool.append('Are there any price discrepancies across vendors?')

    # Select 6-8 diverse suggestions
    if len(suggestion_pool) <= 8:
        selected = suggestion_pool
    else:
        # Always include the first 3 generic ones, then sample the rest
        selected = suggestion_pool[:3]
        remaining = suggestion_pool[3:]
        random.shuffle(remaining)
        selected.extend(remaining[:5])

    return jsonify({'suggestions': selected})
