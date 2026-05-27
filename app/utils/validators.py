"""
Form validation utilities.

Each validator returns a tuple of (is_valid: bool, error_message: str).
If is_valid is True, error_message is empty.
"""

import re


def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate a username.

    Rules:
    - 3-50 characters
    - Alphanumeric and underscores only
    - Cannot start with a number
    """
    if not username:
        return False, "Username is required."

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if len(username) > 50:
        return False, "Username cannot exceed 50 characters."

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", username):
        return False, (
            "Username must start with a letter and contain only "
            "letters, numbers, and underscores."
        )

    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate an email address.

    Uses a simple but practical regex - not RFC-compliant but catches
    the most common errors. Real email verification requires sending a
    confirmation email anyway.
    """
    if not email:
        return False, "Email is required."

    if len(email) > 120:
        return False, "Email cannot exceed 120 characters."

    # Simple pattern: something@something.something
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Please enter a valid email address."

    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate a password.

    Rules:
    - At least 8 characters
    - At least one letter
    - At least one number

    Note: We deliberately don't require special characters - NIST guidelines
    now recommend longer passwords over complexity rules.
    """
    if not password:
        return False, "Password is required."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    if len(password) > 128:
        return False, "Password is too long (max 128 characters)."

    if not re.search(r"[a-zA-Z]", password):
        return False, "Password must contain at least one letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    return True, ""


def validate_project_name(name: str) -> tuple[bool, str]:
    """
    Validate a project name.

    Rules:
    - 1-100 characters
    - Cannot be only whitespace
    """
    if not name or not name.strip():
        return False, "Project name is required."

    if len(name) > 100:
        return False, "Project name cannot exceed 100 characters."

    return True, ""


def validate_project_description(description: str) -> tuple[bool, str]:
    """
    Validate a project description.

    Description is optional but if provided, has a length limit.
    Stored as TEXT in DB but we cap at a reasonable UI length.
    """
    if description and len(description) > 2000:
        return False, "Project description cannot exceed 2000 characters."

    return True, ""


def validate_task_title(title: str) -> tuple[bool, str]:
    """
    Validate a task title.

    Rules:
    - 1-200 characters
    - Cannot be only whitespace
    """
    if not title or not title.strip():
        return False, "Task title is required."

    if len(title) > 200:
        return False, "Task title cannot exceed 200 characters."

    return True, ""


def validate_task_description(description: str) -> tuple[bool, str]:
    """Validate a task description (optional, length-capped)."""
    if description and len(description) > 5000:
        return False, "Task description cannot exceed 5000 characters."

    return True, ""


def validate_task_status(status: str) -> tuple[bool, str]:
    """Validate that a status value is one of the allowed values."""
    # Import here to avoid circular imports at module load time
    from app.models.task import VALID_STATUSES

    if status not in VALID_STATUSES:
        return False, "Invalid status value."

    return True, ""


def validate_task_priority(priority: str) -> tuple[bool, str]:
    """Validate that a priority value is one of the allowed values."""
    from app.models.task import VALID_PRIORITIES

    if priority not in VALID_PRIORITIES:
        return False, "Invalid priority value."

    return True, ""


def validate_task_due_date(due_date_str: str):
    """
    Validate and parse an optional due date string.

    Accepts empty string or YYYY-MM-DD format.
    Returns (is_valid, error_or_date) where on success the second
    element is a date object (or None for empty), on failure it's an
    error string.
    """
    from datetime import datetime

    if not due_date_str:
        return True, None

    try:
        parsed = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return True, parsed
    except ValueError:
        return False, "Invalid due date. Use YYYY-MM-DD format."
