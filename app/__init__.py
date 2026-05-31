from flask import Flask

from app.config import get_config
from app.cli import register_cli_commands
from app.database import db
from app.routes.health import health_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())
    app.json.compact = app.config["JSON_COMPACT"]
    db.init_app(app)

    app.register_blueprint(health_bp)
    register_cli_commands(app)

    return app
