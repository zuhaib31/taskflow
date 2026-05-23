"""
Custom decorators for route protection.

@login_required - Redirects to login page if user is not authenticated.
"""

from functools import wraps

from flask import session, redirect, url_for, request, flash


def login_required(view_func):
    """
    Decorator that requires the user to be logged in.

    If they're not, redirects to the login page with a 'next' parameter
    so they return to the protected page after login.

    Usage:
        @bp.route("/dashboard")
        @login_required
        def dashboard():
            ...
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.", "info")
            return redirect(url_for("auth.login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped_view
