"""
Project model - represents a project owned by a user.

A project is a container for tasks. Each project belongs to exactly
one user, and users can only access their own projects.

Security note: All query methods require user_id to enforce ownership
at the data layer. This prevents IDOR (Insecure Direct Object Reference)
attacks where a user could access another user's project by guessing IDs.
"""

from app import mysql


class Project:
    """Represents a project owned by a user."""

    def __init__(self, id=None, user_id=None, name=None, description=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def find_by_id_and_user(cls, project_id: int, user_id: int):
        """
        Find a project by ID, but only if it belongs to the given user.

        Returns Project or None. Returns None even if the project exists
        but belongs to a different user - this prevents users from
        learning which IDs are taken by others.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, user_id, name, description, created_at, updated_at "
            "FROM projects WHERE id = %s AND user_id = %s",
            (project_id, user_id)
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return None
        return cls(**row)

    @classmethod
    def find_all_by_user(cls, user_id: int) -> list:
        """
        Return a list of all projects belonging to the given user.

        Ordered by most recently updated first (most relevant to the user).
        Returns an empty list if the user has no projects.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, user_id, name, description, created_at, updated_at "
            "FROM projects WHERE user_id = %s "
            "ORDER BY updated_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()

        return [cls(**row) for row in rows]

    @classmethod
    def count_by_user(cls, user_id: int) -> int:
        """Return the total number of projects owned by the user."""
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS count FROM projects WHERE user_id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row["count"] if row else 0

    def save(self) -> int:
        """
        Insert a new project into the database.

        Returns the new project's ID. The caller must have set
        user_id, name, and optionally description before calling.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO projects (user_id, name, description) "
            "VALUES (%s, %s, %s)",
            (self.user_id, self.name, self.description)
        )
        mysql.connection.commit()
        self.id = cursor.lastrowid
        cursor.close()
        return self.id

    def update(self) -> None:
        """
        Update this project's name and description in the database.

        Only updates if the project's user_id matches (additional
        safety on top of ownership filtering at query time).
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE projects SET name = %s, description = %s "
            "WHERE id = %s AND user_id = %s",
            (self.name, self.description, self.id, self.user_id)
        )
        mysql.connection.commit()
        cursor.close()

    def delete(self) -> None:
        """
        Delete this project from the database.

        Note: tasks and comments belonging to this project will
        be automatically deleted by the ON DELETE CASCADE constraint
        defined in our schema.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "DELETE FROM projects WHERE id = %s AND user_id = %s",
            (self.id, self.user_id)
        )
        mysql.connection.commit()
        cursor.close()
