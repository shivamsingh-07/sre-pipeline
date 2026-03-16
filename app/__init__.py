"""Application factory."""

import logging
import os
from flask import Flask

from app.config import Config
from app.extensions import db, migrate
from app.web import web_bp
from app.api.v1 import api_v1

# Migrations folder at project root (parent of app/)
MIGRATIONS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "migrations")
)


def configure_logging(app: Flask) -> None:
    """Configure app logger with format and level."""
    level = getattr(
        logging, (os.environ.get("LOG_LEVEL", "INFO")).upper(), logging.INFO
    )
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=level, format=fmt, datefmt=datefmt)
    # Reduce noise from third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    app.logger.setLevel(level)


def create_app(config_overrides: dict | None = None) -> Flask:
    flask_app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )
    flask_app.config.from_object(Config)
    if config_overrides:
        flask_app.config.update(config_overrides)
    configure_logging(flask_app)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db, directory=MIGRATIONS_DIR)

    with flask_app.app_context():
        import app.models  # noqa: F401 — register models for migrations

    flask_app.register_blueprint(web_bp, url_prefix="/")
    flask_app.register_blueprint(api_v1, url_prefix="/api/v1")

    return flask_app
