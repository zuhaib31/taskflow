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
from app.models.task import Task
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

    Shows all of the user's projects and task statistics across
    all projects.
    """
    user_id = session["user_id"]
    user = User.find_by_id(user_id)
    projects = Project.find_all_by_user(user_id)
    task_stats = Task.stats_by_user(user_id)

    return render_template(
        "dashboard.html",
        user=user,
        projects=projects,
        task_stats=task_stats,
    )
