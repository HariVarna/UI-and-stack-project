"""
database/db.py - SQLite Database management module for the Flask application.
"""
import os
import sqlite3
try:
    from flask import g
except ImportError:
    g = None

# Path to the SQLite database file and schema file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "auth.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")


def get_db():
    """
    Opens a connection to the SQLite database.
    If called within a Flask application context, it stores and reuses
    the connection in Flask's 'g' object for the lifecycle of the request.
    """
    # Check if we are inside a Flask request context
    if g is not None and "db" in g:
        return g.db

    # Create new connection
    conn = sqlite3.connect(DATABASE_PATH)
    # Enable access to columns by name like a dictionary (e.g., row['email'])
    conn.row_factory = sqlite3.Row

    if g is not None:
        g.db = conn

    return conn


def close_db(e=None):
    """
    Closes the database connection at the end of a request context.
    """
    if g is not None and "db" in g:
        db = g.pop("db", None)
        if db is not None:
            db.close()


def init_db():
    """
    Executes the schema.sql script to initialize tables in SQLite database.
    """
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    with open(SCHEMA_PATH, mode="r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"[OK] Database successfully initialized at: {DATABASE_PATH}")


def init_app(app):
    """
    Registers database teardown and custom CLI command with the Flask app.
    """
    app.teardown_appcontext(close_db)

    # Register 'flask init-db' CLI command
    @app.cli.command("init-db")
    def init_db_command():
        """Initialize the SQLite database."""
        init_db()
        print("Initialized the database via Flask CLI.")


if __name__ == "__main__":
    # Allows running `python database/db.py` directly from the terminal
    init_db()
