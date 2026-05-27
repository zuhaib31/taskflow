"""
Task model - represents a task within a project.

Tasks belong to projects, which belong to users. Authorization is
enforced through the project chain: we verify the parent project
belongs to the requesting user before granting access to any task.

Status values: 'todo', 'in_progress', 'done'
Priority values: 'low', 'medium', 'high'
"""

from app import mysql


# Valid values - enforced both here and at the database (ENUM)
VALID_STATUSES = ("todo", "in_progress", "done")
VALID_PRIORITIES = ("low", "medium", "high")


class Task:
    """Represents a task within a project."""

    def __init__(self, id=None, project_id=None, title=None, description=None,
                 status="todo", priority="medium", due_date=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.due_date = due_date
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def find_by_id_and_project(cls, task_id: int, project_id: int):
        """
        Find a task by ID, but only if it belongs to the given project.

        Returns Task or None. The caller is responsible for verifying
        that the project belongs to the current user.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, project_id, title, description, status, priority, "
            "due_date, created_at, updated_at "
            "FROM tasks WHERE id = %s AND project_id = %s",
            (task_id, project_id)
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return None
        return cls(**row)

    @classmethod
    def find_all_by_project(cls, project_id: int) -> list:
        """
        Return all tasks in a project, ordered by status then priority.

        Order: todo first, then in_progress, then done.
        Within each status, high priority first.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, project_id, title, description, status, priority, "
            "due_date, created_at, updated_at "
            "FROM tasks WHERE project_id = %s "
            "ORDER BY "
            "  FIELD(status, 'todo', 'in_progress', 'done'), "
            "  FIELD(priority, 'high', 'medium', 'low'), "
            "  created_at DESC",
            (project_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return [cls(**row) for row in rows]

    @classmethod
    def stats_by_user(cls, user_id: int) -> dict:
        """
        Return task counts grouped by status for all of a user's tasks.

        Used by the dashboard to show overall progress. Joins through
        the projects table to scope to the user's tasks only.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT t.status, COUNT(*) AS count "
            "FROM tasks t "
            "INNER JOIN projects p ON p.id = t.project_id "
            "WHERE p.user_id = %s "
            "GROUP BY t.status",
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()

        # Initialize all statuses to 0 so the template doesn't need to handle missing keys
        stats = {"todo": 0, "in_progress": 0, "done": 0, "total": 0}
        for row in rows:
            status = row["status"]
            count = row["count"]
            stats[status] = count
            stats["total"] += count

        return stats

    def save(self) -> int:
        """
        Insert this task into the database.

        Returns the new task's ID. The caller must have set
        project_id and title before calling.
        """
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO tasks "
            "(project_id, title, description, status, priority, due_date) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (self.project_id, self.title, self.description,
             self.status, self.priority, self.due_date)
        )
        mysql.connection.commit()
        self.id = cursor.lastrowid
        cursor.close()
        return self.id

    def update(self) -> None:
        """Update this task's fields in the database."""
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE tasks "
            "SET title = %s, description = %s, status = %s, "
            "    priority = %s, due_date = %s "
            "WHERE id = %s AND project_id = %s",
            (self.title, self.description, self.status,
             self.priority, self.due_date, self.id, self.project_id)
        )
        mysql.connection.commit()
        cursor.close()

    def delete(self) -> None:
        """Delete this task. Comments are removed via ON DELETE CASCADE."""
        cursor = mysql.connection.cursor()
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND project_id = %s",
            (self.id, self.project_id)
        )
        mysql.connection.commit()
        cursor.close()
