"""
Main blueprint - public routes and the user dashboard.

Routes:
- GET /         : Public landing page
- GET /health   : Health check endpoint (Docker/Jenkins/monitoring)
- GET /dashboard: User dashboard (login required)
"""

from flask import Blueprint, jsonify, render_template, session, redirect, url_for

from app.models.user import User
from app.models.project import Project
from app.utils.decorators import login_required

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
    """
    Landing page - publicly accessible.

    If a user is already logged in, redirect them to their dashboard.
    """
    if session.get("user_id"):
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    """
    User's main dashboard - requires authentication.

    Shows all of the user's projects and overall task statistics.
    """
    user_id = session["user_id"]
    user = User.find_by_id(user_id)
    projects = Project.find_all_by_user(user_id)

    # Task stats are still placeholders - will be wired up in Phase 5
    task_stats = {
        "total": 0,
        "todo": 0,
        "in_progress": 0,
        "done": 0,
    }

    return render_template(
        "dashboard.html",
        user=user,
        projects=projects,
        task_stats=task_stats,
    )
