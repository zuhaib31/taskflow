"""
Initialize the database by running the SQL migration files.

Usage:
    python scripts/init_db.py

This script is intended for local development and initial setup.
In production, migrations should be run by your deployment pipeline.
"""

import os
import sys

# Make sure we can import from the app package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, mysql


def run_migrations():
    """Run all .sql files in the migrations/ directory in order."""
    app = create_app()
    migrations_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "migrations",
    )

    migration_files = sorted(
        f for f in os.listdir(migrations_dir) if f.endswith(".sql")
    )

    if not migration_files:
        print("No migration files found.")
        return

    with app.app_context():
        cursor = mysql.connection.cursor()
        for filename in migration_files:
            print(f"Running migration: {filename}")
            filepath = os.path.join(migrations_dir, filename)
            with open(filepath, "r") as f:
                sql = f.read()

            # Execute each statement separated by semicolons
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement and not statement.startswith("--"):
                    cursor.execute(statement)

            mysql.connection.commit()
            print(f"  ✓ {filename} completed")

        cursor.close()
    print("\nAll migrations completed successfully.")


if __name__ == "__main__":
    run_migrations()