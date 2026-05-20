"""
Configuration management for TaskFlow.

Defines configuration classes for different environments
(development, testing, production) following the 12-Factor App methodology.
All sensitive values are loaded from environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Base configuration with values shared across all environments."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-do-not-use-in-prod")

    # MySQL
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "taskflow")
    MYSQL_CURSORCLASS = "DictCursor"  # Return rows as dicts, not tuples

    # Application
    APP_PORT = int(os.environ.get("APP_PORT", 5000))


class DevelopmentConfig(Config):
    """Configuration for local development."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configuration for running automated tests."""

    DEBUG = False
    TESTING = True
    MYSQL_DB = "taskflow_test"


class ProductionConfig(Config):
    """Configuration for production deployment."""

    DEBUG = False
    TESTING = False

    @classmethod
    def init_app(cls, app):
        """Validate required production environment variables are set."""
        required = ["SECRET_KEY", "MYSQL_PASSWORD"]
        missing = [var for var in required if not os.environ.get(var)]
        if missing:
            raise RuntimeError(
                f"Missing required environment variables for production: {missing}"
            )


# Configuration map - looked up by name
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}