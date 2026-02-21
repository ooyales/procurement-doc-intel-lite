import os
from flask import Flask
from sqlalchemy import BigInteger
from sqlalchemy.ext.compiler import compiles
from flasgger import Swagger
from app.config import config
from app.extensions import db, jwt, cors
from app.errors import register_error_handlers


@compiles(BigInteger, 'sqlite')
def _render_bigint_as_int(type_, compiler, **kw):
    return 'INTEGER'


SWAGGER_TEMPLATE = {
    "info": {
        "title": "Procurement Doc Intel Lite API",
        "description": "API for Procurement Document Intelligence — document upload, AI extraction & field mapping, line item search, spend analysis, RAG chat, and IGCE calculator.",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Enter: **Bearer {your-jwt-token}**"
        }
    },
    "security": [{"Bearer": []}],
    "basePath": "/",
    "schemes": ["http", "https"],
    "definitions": {
        "Error": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "display_name": {"type": "string"},
                "email": {"type": "string"},
                "role": {"type": "string", "enum": ["admin", "viewer"]}
            }
        },
        "Document": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "original_filename": {"type": "string"},
                "file_format": {"type": "string", "enum": ["pdf", "xlsx", "docx", "csv"]},
                "file_size_bytes": {"type": "integer"},
                "file_hash": {"type": "string"},
                "stored_path": {"type": "string"},
                "document_type": {"type": "string"},
                "vendor_name": {"type": "string"},
                "document_number": {"type": "string"},
                "document_date": {"type": "string"},
                "contract_number": {"type": "string"},
                "task_order_number": {"type": "string"},
                "period_of_performance_start": {"type": "string"},
                "period_of_performance_end": {"type": "string"},
                "total_amount": {"type": "number"},
                "currency": {"type": "string"},
                "processing_status": {"type": "string", "enum": ["uploaded", "extracting", "mapping", "review", "complete", "failed"]},
                "extraction_method": {"type": "string"},
                "extraction_confidence": {"type": "number"},
                "ai_model_used": {"type": "string"},
                "reviewed_by": {"type": "string"},
                "reviewed_at": {"type": "string"},
                "review_notes": {"type": "string"},
                "chunk_count": {"type": "integer"},
                "embedded": {"type": "integer"},
                "uploaded_by": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": "string", "format": "date-time"},
                "tags": {"type": "string"},
                "notes": {"type": "string"},
                "line_item_count": {"type": "integer"}
            }
        },
        "LineItem": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "document_id": {"type": "string", "format": "uuid"},
                "line_number": {"type": "integer"},
                "clin": {"type": "string"},
                "slin": {"type": "string"},
                "part_number": {"type": "string"},
                "manufacturer": {"type": "string"},
                "manufacturer_part_number": {"type": "string"},
                "product_name": {"type": "string"},
                "product_description": {"type": "string"},
                "category": {"type": "string"},
                "sub_category": {"type": "string"},
                "quantity": {"type": "number"},
                "unit_of_issue": {"type": "string"},
                "unit_price": {"type": "number"},
                "extended_price": {"type": "number"},
                "discount_percent": {"type": "number"},
                "discount_amount": {"type": "number"},
                "labor_category": {"type": "string"},
                "labor_hours": {"type": "number"},
                "labor_rate": {"type": "number"},
                "period_start": {"type": "string"},
                "period_end": {"type": "string"},
                "mapping_confidence": {"type": "number"},
                "human_verified": {"type": "integer"},
                "original_row_text": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"},
                "vendor_name": {"type": "string"},
                "document_number": {"type": "string"},
                "document_type": {"type": "string"},
                "document_date": {"type": "string"},
                "original_filename": {"type": "string"}
            }
        },
        "CanonicalProduct": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "canonical_name": {"type": "string"},
                "category": {"type": "string"},
                "manufacturer": {"type": "string"},
                "known_part_numbers": {"type": "array", "items": {"type": "string"}},
                "known_aliases": {"type": "array", "items": {"type": "string"}},
                "last_known_price": {"type": "number"},
                "last_price_date": {"type": "string"},
                "avg_price": {"type": "number"},
                "min_price": {"type": "number"},
                "max_price": {"type": "number"},
                "price_history": {"type": "array", "items": {"type": "object"}},
                "asset_tracker_category": {"type": "string"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        "DocumentChunk": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "document_id": {"type": "string", "format": "uuid"},
                "chunk_index": {"type": "integer"},
                "content": {"type": "string"},
                "chunk_type": {"type": "string"},
                "page_number": {"type": "integer"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        },
        "FieldMapping": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "format": "uuid"},
                "vendor_name": {"type": "string"},
                "source_column_name": {"type": "string"},
                "target_field": {"type": "string"},
                "confidence": {"type": "number"},
                "times_confirmed": {"type": "integer"},
                "created_at": {"type": "string", "format": "date-time"}
            }
        }
    }
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: rule.rule.startswith('/api/'),
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', '/app/uploads'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)

    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    # Register blueprints
    from app.api import register_blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Create tables and init FTS5
    with app.app_context():
        db.create_all()
        _init_fts5()

    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        """Health check endpoint.
        ---
        tags:
          - System
        security: []
        responses:
          200:
            description: Service is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
                timestamp:
                  type: string
                  format: date-time
                app:
                  type: string
                  example: procurement-doc-intel-lite
        """
        from flask import jsonify
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'app': 'procurement-doc-intel-lite'
        })

    # Demo auth (enabled via DEMO_AUTH_ENABLED env var)
    try:
        from demo_auth import init_demo_auth
        from demo_sessions import SessionManager
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite:///'):
            template_db = os.path.join(app.instance_path, db_uri.replace('sqlite:///', ''))
        else:
            template_db = os.path.join(app.instance_path, 'procdoc.db')
        _session_mgr = SessionManager(
            template_db=template_db,
            sessions_dir=os.path.join(os.path.dirname(app.instance_path), 'data', 'sessions')
        )
        init_demo_auth(app, session_manager=_session_mgr)
    except ImportError:
        pass

    # Register CLI commands
    register_cli(app)

    return app


def _init_fts5():
    """Create FTS5 virtual table for document chunk search if it doesn't exist."""
    from sqlalchemy import text
    try:
        db.session.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS document_chunks_fts
            USING fts5(content, content='document_chunks', content_rowid='rowid')
        """))
        db.session.commit()
    except Exception:
        db.session.rollback()


def register_cli(app):
    @app.cli.command('seed')
    def seed_command():
        """Seed the database with sample data."""
        from app.seed import seed
        seed()
        print('Database seeded.')

    @app.cli.command('init-db')
    def init_db_command():
        """Create all database tables."""
        db.create_all()
        _init_fts5()
        print('Database initialized.')

    @app.cli.command('reset-db')
    def reset_db_command():
        """Drop and recreate all database tables, then seed."""
        db.drop_all()
        db.create_all()
        _init_fts5()
        from app.seed import seed
        seed()
        print('Database reset and seeded.')
