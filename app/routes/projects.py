"""
Projects blueprint - CRUD operations for projects.

All routes require authentication and enforce ownership at the
model layer (Project.find_by_id_and_user). A user can never
access another user's project, even by guessing IDs.

Routes:
- GET  /projects              : List all of the user's projects
- GET  /projects/new          : Show new project form
- POST /projects              : Create a new project
- GET  /projects/<id>         : Show a single project
- GET  /projects/<id>/edit    : Show edit form
- POST /projects/<id>         : Update a project
- POST /projects/<id>/delete  : Delete a project
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, abort
)

from app.models.project import Project
from app.models.task import Task
from app.utils.decorators import login_required
from app.utils.validators import (
    validate_project_name, validate_project_description
)

bp = Blueprint("projects", __name__, url_prefix="/projects")


@bp.route("/")
@login_required
def index():
    """List all projects owned by the current user."""
    projects = Project.find_all_by_user(session["user_id"])
    return render_template("projects/index.html", projects=projects)


@bp.route("/new", methods=["GET"])
@login_required
def new():
    """Show the form to create a new project."""
    return render_template("projects/new.html")


@bp.route("/", methods=["POST"])
@login_required
def create():
    """Process the new project form submission."""
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip() or None

    is_valid, error_msg = validate_project_name(name)
    if not is_valid:
        flash(error_msg, "error")
        return render_template(
            "projects/new.html",
            name=name,
            description=description,
        )

    is_valid, error_msg = validate_project_description(description or "")
    if not is_valid:
        flash(error_msg, "error")
        return render_template(
            "projects/new.html",
            name=name,
            description=description,
        )

    project = Project(
        user_id=session["user_id"],
        name=name,
        description=description,
    )
    project.save()

    flash(f"Project '{project.name}' created successfully.", "success")
    return redirect(url_for("projects.show", project_id=project.id))


@bp.route("/<int:project_id>")
@login_required
def show(project_id):
    """Show a single project with its tasks grouped by status."""
    project = Project.find_by_id_and_user(project_id, session["user_id"])
    if project is None:
        abort(404)

    tasks = Task.find_all_by_project(project.id)

    # Group tasks by status for column-style display
    tasks_by_status = {
        "todo": [t for t in tasks if t.status == "todo"],
        "in_progress": [t for t in tasks if t.status == "in_progress"],
        "done": [t for t in tasks if t.status == "done"],
    }

    return render_template(
        "projects/show.html",
        project=project,
        tasks=tasks,
        tasks_by_status=tasks_by_status,
    )


@bp.route("/<int:project_id>/edit", methods=["GET"])
@login_required
def edit(project_id):
    """Show the edit form for a project."""
    project = Project.find_by_id_and_user(project_id, session["user_id"])
    if project is None:
        abort(404)

    return render_template("projects/edit.html", project=project)


@bp.route("/<int:project_id>", methods=["POST"])
@login_required
def update(project_id):
    """Process the edit form submission."""
    project = Project.find_by_id_and_user(project_id, session["user_id"])
    if project is None:
        abort(404)

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip() or None

    is_valid, error_msg = validate_project_name(name)
    if not is_valid:
        flash(error_msg, "error")
        project.name = name
        project.description = description
        return render_template("projects/edit.html", project=project)

    is_valid, error_msg = validate_project_description(description or "")
    if not is_valid:
        flash(error_msg, "error")
        project.name = name
        project.description = description
        return render_template("projects/edit.html", project=project)

    project.name = name
    project.description = description
    project.update()

    flash("Project updated successfully.", "success")
    return redirect(url_for("projects.show", project_id=project.id))


@bp.route("/<int:project_id>/delete", methods=["POST"])
@login_required
def destroy(project_id):
    """Delete a project (cascades to tasks and comments)."""
    project = Project.find_by_id_and_user(project_id, session["user_id"])
    if project is None:
        abort(404)

    project_name = project.name
    project.delete()

    flash(f"Project '{project_name}' was deleted.", "info")
    return redirect(url_for("main.dashboard"))
