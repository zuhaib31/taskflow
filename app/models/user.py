"""
User model - represents a user account in the database.

Handles password hashing/verification and provides class methods
for common database operations like finding a user by email.
"""

from werkzeug.security import generate_password_hash, check_password_hash

from app import mysql


class User:
    """Represents a user account."""

    def __init__(self, id=None, username=None, email=None, password_hash=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a plain-text password using Werkzeug's secure hashing.

        Uses PBKDF2 with SHA-256 by default, which is industry-standard
        for password storage. Each hash includes a random salt.
        """
        return generate_password_hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        """
        Check if a plain-text password matches this user's stored hash.

        Returns True if match, False otherwise.
        Uses constant-time comparison to prevent timing attacks.
        """
        return check_password_hash(self.password_hash, plain_password)

    @classmethod
    def find_by_email(cls, email: str):
        """Find a user by their email address. Returns User or None."""
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, created_at, updated_at "
            "FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return None
        return cls(**row)

    @classmethod
    def find_by_username(cls, username: str):
        """Find a user by their username. Returns User or None."""
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, created_at, updated_at "
            "FROM users WHERE username = %s",
            (username,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return None
        return cls(**row)

    @classmethod
    def find_by_id(cls, user_id: int):
        """Find a user by their ID. Returns User or None."""
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, created_at, updated_at "
            "FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return None
        return cls(**row)

    def save(self) -> int:
        """
        Insert this user into the database.

        Returns the new user's ID. Raises an exception if email/username
        already exists (caught by the route handler).
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) "
            "VALUES (%s, %s, %s)",
            (self.username, self.email, self.password_hash)
        )
        mysql.connection.commit()
        self.id = cursor.lastrowid
        cursor.close()
        return self.id
