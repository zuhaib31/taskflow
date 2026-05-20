"""
Main blueprint - public routes that don't require authentication.

Includes:
- Health check endpoint (for Docker/Jenkins/monitoring)
- Home/landing page
"""

from flask import Blueprint, jsonify, render_template

bp = Blueprint("main", __name__)


@bp.route("/health")
def health():
    """
    Health check endpoint.

    Used by:
    - Docker healthcheck directive
    - Load balancers / monitoring systems
    - Jenkins post-deployment verification

    Returns minimal JSON to keep it fast.
    """
    return jsonify({"status": "healthy", "service": "taskflow"}), 200


@bp.route("/")
def index():
    """Landing page - publicly accessible."""
    return render_template("index.html")
