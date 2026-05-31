from flask import Flask

from app.config import get_config
from app.cli import register_cli_commands
from app.database import db
from app.routes.clients import clients_bp
from app.routes.health import health_bp
from app.routes.orders import orders_bp
from app.routes.products import products_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.json.compact = app.config["JSON_COMPACT"]
    db.init_app(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(clients_bp, url_prefix="/api/clients")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    register_cli_commands(app)

    return app
