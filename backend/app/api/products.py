import json
import logging
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.canonical_product import CanonicalProduct
from app.models.line_item import LineItem
from app.models.document import Document
from app.errors import BadRequestError, NotFoundError

logger = logging.getLogger(__name__)

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    """List canonical products with optional search and pagination.
    ---
    tags:
      - Products
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number
      - name: per_page
        in: query
        type: integer
        required: false
        default: 25
        description: Items per page (max 100)
      - name: search
        in: query
        type: string
        required: false
        description: Search across canonical name, manufacturer, category
      - name: category
        in: query
        type: string
        required: false
        description: Filter by product category
    responses:
      200:
        description: Paginated list of canonical products
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                $ref: '#/definitions/CanonicalProduct'
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)

    query = CanonicalProduct.query.filter_by(session_id='__default__')

    search = request.args.get('search', '').strip()
    if search:
        search_filter = f'%{search}%'
        query = query.filter(
            db.or_(
                CanonicalProduct.canonical_name.ilike(search_filter),
                CanonicalProduct.manufacturer.ilike(search_filter),
                CanonicalProduct.category.ilike(search_filter),
            )
        )

    # Optional category filter
    category = request.args.get('category', '').strip()
    if category:
        query = query.filter(CanonicalProduct.category == category)

    query = query.order_by(CanonicalProduct.canonical_name)
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'items': [p.to_dict() for p in products],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@products_bp.route('/<product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get a single canonical product with full details and recent line items.
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: string
        required: true
        description: Canonical product UUID
    responses:
      200:
        description: Product details with recent line items
        schema:
          allOf:
            - $ref: '#/definitions/CanonicalProduct'
            - type: object
              properties:
                recent_line_items:
                  type: array
                  items:
                    $ref: '#/definitions/LineItem'
                line_item_count:
                  type: integer
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Product not found
        schema:
          $ref: '#/definitions/Error'
    """
    product = CanonicalProduct.query.get(product_id)
    if not product:
        raise NotFoundError(f'Product {product_id} not found')

    result = product.to_dict()

    # Include recent line items for this product
    line_items = LineItem.query.join(Document, LineItem.document_id == Document.id)\
        .filter(LineItem.session_id == '__default__')\
        .filter(LineItem.product_name == product.canonical_name)\
        .order_by(LineItem.created_at.desc())\
        .limit(20)\
        .all()

    result['recent_line_items'] = [li.to_dict() for li in line_items]
    result['line_item_count'] = LineItem.query.filter_by(
        product_name=product.canonical_name,
        session_id='__default__',
    ).count()

    return jsonify(result)


@products_bp.route('/<product_id>/igce', methods=['POST'])
@jwt_required()
def generate_igce(product_id):
    """Generate IGCE (Independent Government Cost Estimate) for a product.
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: string
        required: true
        description: Canonical product UUID
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            quantity:
              type: number
              default: 1
              description: Quantity to estimate
            escalation_rate:
              type: number
              default: 0.03
              description: Price escalation rate (e.g. 0.03 for 3%)
    responses:
      200:
        description: IGCE calculation result with price sources
        schema:
          type: object
          properties:
            product_name:
              type: string
            category:
              type: string
            manufacturer:
              type: string
            quantity:
              type: number
            avg_unit_price:
              type: number
            min_price:
              type: number
            max_price:
              type: number
            escalation_rate:
              type: number
            estimated_unit_price:
              type: number
            estimated_total:
              type: number
            price_sources:
              type: array
              items:
                type: object
                properties:
                  price:
                    type: number
                  date:
                    type: string
                  vendor:
                    type: string
            data_points:
              type: integer
      400:
        description: Invalid parameters or no pricing data available
        schema:
          $ref: '#/definitions/Error'
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
      404:
        description: Product not found
        schema:
          $ref: '#/definitions/Error'
    """
    product = CanonicalProduct.query.get(product_id)
    if not product:
        raise NotFoundError(f'Product {product_id} not found')

    data = request.get_json() or {}
    quantity = data.get('quantity', 1)
    escalation_rate = data.get('escalation_rate', 0.03)

    if not isinstance(quantity, (int, float)) or quantity <= 0:
        raise BadRequestError('Quantity must be a positive number')
    if not isinstance(escalation_rate, (int, float)) or escalation_rate < 0:
        raise BadRequestError('Escalation rate must be a non-negative number')

    avg_price = product.avg_price or product.last_known_price
    if avg_price is None:
        raise BadRequestError(f'No pricing data available for product "{product.canonical_name}"')

    # Apply escalation: estimated_unit_price = avg_price * (1 + escalation_rate)
    estimated_unit_price = round(avg_price * (1 + escalation_rate), 2)
    estimated_total = round(estimated_unit_price * quantity, 2)

    # Gather price sources from line items
    price_sources_query = db.session.query(
        LineItem.unit_price,
        Document.document_date,
        Document.vendor_name,
    ).join(Document, LineItem.document_id == Document.id)\
     .filter(LineItem.session_id == '__default__')\
     .filter(LineItem.product_name == product.canonical_name)\
     .filter(LineItem.unit_price.isnot(None))\
     .order_by(Document.document_date.desc())\
     .limit(20)\
     .all()

    price_sources = [
        {
            'price': round(row[0], 2) if row[0] else None,
            'date': row[1],
            'vendor': row[2],
        }
        for row in price_sources_query
    ]

    return jsonify({
        'product_name': product.canonical_name,
        'category': product.category,
        'manufacturer': product.manufacturer,
        'quantity': quantity,
        'avg_unit_price': round(avg_price, 2),
        'min_price': round(product.min_price, 2) if product.min_price else None,
        'max_price': round(product.max_price, 2) if product.max_price else None,
        'escalation_rate': escalation_rate,
        'estimated_unit_price': estimated_unit_price,
        'estimated_total': estimated_total,
        'price_sources': price_sources,
        'data_points': len(price_sources),
    })


@products_bp.route('/rebuild', methods=['POST'])
@jwt_required()
def rebuild_catalog():
    """Rebuild canonical product catalog from line items.
    ---
    tags:
      - Products
    responses:
      200:
        description: Catalog rebuild summary
        schema:
          type: object
          properties:
            message:
              type: string
            created:
              type: integer
              description: Number of new products created
            updated:
              type: integer
              description: Number of existing products updated
            total:
              type: integer
              description: Total products in catalog
      401:
        description: Unauthorized
        schema:
          $ref: '#/definitions/Error'
    """
    session_filter = '__default__'

    # Group line items by product_name and compute statistics
    product_stats = db.session.query(
        LineItem.product_name,
        LineItem.category,
        LineItem.manufacturer,
        LineItem.part_number,
        db.func.avg(LineItem.unit_price).label('avg_price'),
        db.func.min(LineItem.unit_price).label('min_price'),
        db.func.max(LineItem.unit_price).label('max_price'),
        db.func.count(LineItem.id).label('item_count'),
    ).filter_by(session_id=session_filter)\
     .filter(LineItem.product_name.isnot(None))\
     .filter(LineItem.product_name != '')\
     .group_by(LineItem.product_name)\
     .all()

    created = 0
    updated = 0

    for stat in product_stats:
        product_name = stat[0]
        category = stat[1]
        manufacturer = stat[2]
        part_number = stat[3]
        avg_price = stat[4]
        min_price = stat[5]
        max_price = stat[6]

        # Check if canonical product already exists
        existing = CanonicalProduct.query.filter_by(
            canonical_name=product_name,
            session_id=session_filter,
        ).first()

        # Get the latest price and date
        latest_item = LineItem.query.join(Document, LineItem.document_id == Document.id)\
            .filter(LineItem.session_id == session_filter)\
            .filter(LineItem.product_name == product_name)\
            .filter(LineItem.unit_price.isnot(None))\
            .order_by(Document.document_date.desc())\
            .first()

        last_price = latest_item.unit_price if latest_item else None
        last_date = latest_item.document.document_date if latest_item and latest_item.document else None

        # Build price history from individual line items
        price_history_rows = db.session.query(
            LineItem.unit_price,
            Document.document_date,
            Document.vendor_name,
        ).join(Document, LineItem.document_id == Document.id)\
         .filter(LineItem.session_id == session_filter)\
         .filter(LineItem.product_name == product_name)\
         .filter(LineItem.unit_price.isnot(None))\
         .order_by(Document.document_date.asc())\
         .limit(50)\
         .all()

        price_history = [
            {
                'price': round(r[0], 2) if r[0] else None,
                'date': r[1],
                'vendor': r[2],
            }
            for r in price_history_rows
        ]

        # Collect known part numbers
        part_numbers_rows = db.session.query(
            db.distinct(LineItem.part_number),
        ).filter_by(session_id=session_filter)\
         .filter(LineItem.product_name == product_name)\
         .filter(LineItem.part_number.isnot(None))\
         .filter(LineItem.part_number != '')\
         .all()
        known_part_numbers = [r[0] for r in part_numbers_rows if r[0]]

        if existing:
            existing.category = category or existing.category
            existing.manufacturer = manufacturer or existing.manufacturer
            existing.avg_price = round(avg_price, 2) if avg_price else existing.avg_price
            existing.min_price = round(min_price, 2) if min_price else existing.min_price
            existing.max_price = round(max_price, 2) if max_price else existing.max_price
            existing.last_known_price = round(last_price, 2) if last_price else existing.last_known_price
            existing.last_price_date = last_date or existing.last_price_date
            existing.price_history = json.dumps(price_history)
            existing.known_part_numbers = json.dumps(known_part_numbers)
            updated += 1
        else:
            product = CanonicalProduct(
                canonical_name=product_name,
                category=category,
                manufacturer=manufacturer,
                known_part_numbers=json.dumps(known_part_numbers),
                known_aliases=json.dumps([]),
                last_known_price=round(last_price, 2) if last_price else None,
                last_price_date=last_date,
                avg_price=round(avg_price, 2) if avg_price else None,
                min_price=round(min_price, 2) if min_price else None,
                max_price=round(max_price, 2) if max_price else None,
                price_history=json.dumps(price_history),
                session_id=session_filter,
            )
            db.session.add(product)
            created += 1

    db.session.commit()

    return jsonify({
        'message': f'Product catalog rebuilt: {created} created, {updated} updated',
        'created': created,
        'updated': updated,
        'total': created + updated,
    })
