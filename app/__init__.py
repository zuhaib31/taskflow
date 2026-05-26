"""
TaskFlow application factory.

Creates and configures the Flask application instance using the
application factory pattern. This allows different configurations
for development, testing, and production environments.
"""

import os
from datetime import timedelta

from flask import Flask, render_template
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
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Session lifetime - 7 days
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    # Run any config-specific initialization
    if hasattr(config[config_name], "init_app"):
        config[config_name].init_app(app)

    # Initialize extensions with the app
    mysql.init_app(app)

    # Register blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.projects import bp as projects_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)

    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    return app
