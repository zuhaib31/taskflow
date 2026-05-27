"""
Tasks blueprint - CRUD operations for tasks within projects.

Tasks are scoped to projects via nested URLs:
- /projects/<project_id>/tasks/new
- /projects/<project_id>/tasks/<task_id>
- /projects/<project_id>/tasks/<task_id>/edit

Authorization: We always verify the parent project belongs to the
current user before any task operation. If the project check fails,
the user gets a 404 (not "you don't own this") to avoid leaking
information about which IDs exist.
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, abort
)

from app.models.project import Project
from app.models.task import Task, VALID_STATUSES, VALID_PRIORITIES
from app.utils.decorators import login_required
from app.utils.validators import (
    validate_task_title, validate_task_description,
    validate_task_status, validate_task_priority, validate_task_due_date
)

bp = Blueprint("tasks", __name__, url_prefix="/projects/<int:project_id>/tasks")


def _get_owned_project(project_id):
    """
    Helper: fetch a project verifying ownership, or abort 404.

    Used at the top of every task route to enforce authorization
    through the parent project.
    """
    project = Project.find_by_id_and_user(project_id, session["user_id"])
    if project is None:
        abort(404)
    return project


@bp.route("/new", methods=["GET"])
@login_required
def new(project_id):
    """Show the form to create a new task in this project."""
    project = _get_owned_project(project_id)
    return render_template(
        "tasks/new.html",
        project=project,
        valid_statuses=VALID_STATUSES,
        valid_priorities=VALID_PRIORITIES,
    )


@bp.route("/", methods=["POST"])
@login_required
def create(project_id):
    """Process the new task form submission."""
    project = _get_owned_project(project_id)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip() or None
    status = request.form.get("status", "todo")
    priority = request.form.get("priority", "medium")
    due_date_str = request.form.get("due_date", "").strip()

    # Run all validations - collect first error
    validations = [
        validate_task_title(title),
        validate_task_description(description or ""),
        validate_task_status(status),
        validate_task_priority(priority),
    ]

    for is_valid, error_msg in validations:
        if not is_valid:
            flash(error_msg, "error")
            return _render_new_with_input(project, title, description, status, priority, due_date_str)

    # Due date validation returns the parsed date on success
    is_valid, date_or_error = validate_task_due_date(due_date_str)
    if not is_valid:
        flash(date_or_error, "error")
        return _render_new_with_input(project, title, description, status, priority, due_date_str)
    due_date = date_or_error

    # Create and save
    task = Task(
        project_id=project.id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
    )
    task.save()

    flash(f"Task '{task.title}' created.", "success")
    return redirect(url_for("projects.show", project_id=project.id))


@bp.route("/<int:task_id>", methods=["GET"])
@login_required
def show(project_id, task_id):
    """Show a single task's details."""
    project = _get_owned_project(project_id)
    task = Task.find_by_id_and_project(task_id, project.id)
    if task is None:
        abort(404)

    return render_template("tasks/show.html", project=project, task=task)


@bp.route("/<int:task_id>/edit", methods=["GET"])
@login_required
def edit(project_id, task_id):
    """Show the edit form for a task."""
    project = _get_owned_project(project_id)
    task = Task.find_by_id_and_project(task_id, project.id)
    if task is None:
        abort(404)

    return render_template(
        "tasks/edit.html",
        project=project,
        task=task,
        valid_statuses=VALID_STATUSES,
        valid_priorities=VALID_PRIORITIES,
    )


@bp.route("/<int:task_id>", methods=["POST"])
@login_required
def update(project_id, task_id):
    """Process the edit form submission."""
    project = _get_owned_project(project_id)
    task = Task.find_by_id_and_project(task_id, project.id)
    if task is None:
        abort(404)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip() or None
    status = request.form.get("status", "todo")
    priority = request.form.get("priority", "medium")
    due_date_str = request.form.get("due_date", "").strip()

    validations = [
        validate_task_title(title),
        validate_task_description(description or ""),
        validate_task_status(status),
        validate_task_priority(priority),
    ]

    for is_valid, error_msg in validations:
        if not is_valid:
            flash(error_msg, "error")
            return _render_edit_with_input(project, task, title, description, status, priority, due_date_str)

    is_valid, date_or_error = validate_task_due_date(due_date_str)
    if not is_valid:
        flash(date_or_error, "error")
        return _render_edit_with_input(project, task, title, description, status, priority, due_date_str)

    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.due_date = date_or_error
    task.update()

    flash("Task updated.", "success")
    return redirect(url_for("tasks.show", project_id=project.id, task_id=task.id))


@bp.route("/<int:task_id>/delete", methods=["POST"])
@login_required
def destroy(project_id, task_id):
    """Delete a task."""
    project = _get_owned_project(project_id)
    task = Task.find_by_id_and_project(task_id, project.id)
    if task is None:
        abort(404)

    task_title = task.title
    task.delete()

    flash(f"Task '{task_title}' was deleted.", "info")
    return redirect(url_for("projects.show", project_id=project.id))


@bp.route("/<int:task_id>/status", methods=["POST"])
@login_required
def update_status(project_id, task_id):
    """
    Quick status update endpoint.

    Used by status-change buttons on the project detail page so
    users don't need to open the full edit form just to move a
    task to a new column.
    """
    project = _get_owned_project(project_id)
    task = Task.find_by_id_and_project(task_id, project.id)
    if task is None:
        abort(404)

    new_status = request.form.get("status", "")
    is_valid, error_msg = validate_task_status(new_status)
    if not is_valid:
        flash(error_msg, "error")
        return redirect(url_for("projects.show", project_id=project.id))

    task.status = new_status
    task.update()

    return redirect(url_for("projects.show", project_id=project.id))


# ----- Helpers -----

def _render_new_with_input(project, title, description, status, priority, due_date_str):
    """Re-render the new task form with submitted values preserved."""
    return render_template(
        "tasks/new.html",
        project=project,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date_str=due_date_str,
        valid_statuses=VALID_STATUSES,
        valid_priorities=VALID_PRIORITIES,
    )


def _render_edit_with_input(project, task, title, description, status, priority, due_date_str):
    """Re-render the edit task form with submitted values preserved."""
    # Temporarily mutate the task for re-display (not persisted)
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    return render_template(
        "tasks/edit.html",
        project=project,
        task=task,
        due_date_str=due_date_str,
        valid_statuses=VALID_STATUSES,
        valid_priorities=VALID_PRIORITIES,
    )
