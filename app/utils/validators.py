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
