"""
database/db.py - SQLite Database management module for the Flask application.
"""
import os
import sqlite3
try:
    from flask import g, has_app_context
except ImportError:
    g = None
    has_app_context = lambda: False

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
    if has_app_context():
        if "db" not in g:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row
            g.db = conn
        return g.db

    # Standalone connection when called outside Flask request context
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def close_db(e=None):
    """
    Closes the database connection at the end of a request context.
    """
    if has_app_context() and "db" in g:
        db_conn = g.pop("db", None)
        if db_conn is not None:
            db_conn.close()


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
