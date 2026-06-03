"""
Pytest configuration and shared fixtures.

This file is automatically loaded by pytest before any tests run.

We mock the `flask_mysqldb` module here so that the application package
can be imported in environments where the MySQL client library is not
installed (such as local test runs and CI). The validator and route
logic under test does not require a real database connection.
"""

import sys
from unittest.mock import MagicMock

# Insert a mock 'flask_mysqldb' module into sys.modules BEFORE the app
# package is imported. When app/__init__.py runs `from flask_mysqldb
# import MySQL`, it will receive this mock instead of failing.
mock_flask_mysqldb = MagicMock()
sys.modules["flask_mysqldb"] = mock_flask_mysqldb

# Also mock MySQLdb itself, which some modules import directly for
# exception handling (e.g. MySQLdb.IntegrityError in the auth routes).
mock_mysqldb = MagicMock()
# Provide a real exception class so `except MySQLdb.IntegrityError` works.
mock_mysqldb.IntegrityError = type("IntegrityError", (Exception,), {})
mock_mysqldb.cursors = MagicMock()
sys.modules["MySQLdb"] = mock_mysqldb
