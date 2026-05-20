"""
TaskFlow application factory.

Creates and configures the Flask application instance using the
application factory pattern. This allows different configurations
for development, testing, and production environments.
"""

import os
from flask import Flask
from flask_mysqldb import MySQL

from app.config import config

# Initialize MySQL extension here so it can be imported elsewhere.
# It gets bound to the app inside create_app().
mysql = MySQL()


def create_app(config_name: str | None = None) -> Flask:
    """
    Create and configure a Flask application instance.

    Args:
        config_name: Name of configuration to use ('development',
                     'testing', 'production'). Falls back to FLASK_ENV
                     environment variable, then 'development'.

    Returns:
        Configured Flask application instance.
    """
    # Determine configuration to load
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Run any config-specific initialization
    if hasattr(config[config_name], "init_app"):
        config[config_name].init_app(app)

    # Initialize extensions with the app
    mysql.init_app(app)

    # Register blueprints (modular route groups)
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app