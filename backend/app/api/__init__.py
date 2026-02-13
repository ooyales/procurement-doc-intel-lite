from app.api.auth import auth_bp
from app.api.documents import documents_bp
from app.api.line_items import line_items_bp
from app.api.dashboard import dashboard_bp
from app.api.chat import chat_bp
from app.api.products import products_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(line_items_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(products_bp)
