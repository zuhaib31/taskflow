"""
Authentication blueprint - handles registration, login, and logout.

Routes:
- GET/POST /register : User registration
- GET/POST /login    : User login
- POST     /logout   : User logout (POST for CSRF safety)
"""

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session
)
import MySQLdb

from app.models.user import User
from app.utils.validators import (
    validate_username, validate_email, validate_password
)

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Display registration form (GET) or process new user registration (POST)."""

    # If user is already logged in, redirect them away
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate each field
        for value, validator in [
            (username, validate_username),
            (email, validate_email),
            (password, validate_password),
        ]:
            is_valid, error_msg = validator(value)
            if not is_valid:
                flash(error_msg, "error")
                # Re-render form with previously entered values (except password)
                return render_template(
                    "auth/register.html",
                    username=username,
                    email=email,
                )

        # Check uniqueness before attempting insert
        if User.find_by_email(email):
            flash("An account with this email already exists.", "error")
            return render_template("auth/register.html", username=username)

        if User.find_by_username(username):
            flash("This username is already taken.", "error")
            return render_template("auth/register.html", email=email)

        # Create and save the user
        try:
            user = User(
                username=username,
                email=email,
                password_hash=User.hash_password(password),
            )
            user.save()
        except MySQLdb.IntegrityError:
            # Race condition fallback: someone registered with same
            # email/username between our check and insert
            flash("Registration failed. Please try again.", "error")
            return render_template("auth/register.html")

        # Auto-login after registration
        session["user_id"] = user.id
        session["username"] = user.username

        flash(f"Welcome, {user.username}! Your account has been created.", "success")
        return redirect(url_for("main.index"))

    # GET request - just show the empty form
    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Display login form (GET) or authenticate user (POST)."""

    if session.get("user_id"):
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("auth/login.html", email=email)

        user = User.find_by_email(email)

        # IMPORTANT: Use the same error message whether email exists or not.
        # This prevents attackers from learning which emails are registered.
        if user is None or not user.verify_password(password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", email=email)

        # Login successful - create session
        session["user_id"] = user.id
        session["username"] = user.username
        session.permanent = True  # Persists per Flask's PERMANENT_SESSION_LIFETIME

        flash(f"Welcome back, {user.username}!", "success")

        # Redirect to where they came from (if 'next' parameter exists)
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):  # Prevent open redirect
            return redirect(next_page)
        return redirect(url_for("main.index"))

    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
def logout():
    """Log the user out by clearing the session."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
