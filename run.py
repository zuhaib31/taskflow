"""
TaskFlow application entry point.

Run this file to start the development server:
    python run.py

In production, this module is imported by Gunicorn:
    gunicorn run:app
"""

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",      # Listen on all interfaces (required in Docker)
        port=app.config["APP_PORT"],
        debug=app.config["DEBUG"],
    )