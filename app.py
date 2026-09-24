"""
app.py - Main Flask Application for AuthCore Authentication System.
"""
import functools
import os
import re
import secrets
from datetime import datetime, timedelta
import sqlite3

from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
    g
)
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

# Load environment variables from .env file if present
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Security & Session Configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "0") in ("1", "true", "True")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

# Enable CSRF Protection across all POST/PUT/DELETE forms
csrf = CSRFProtect(app)

# Register database helpers and CLI commands with the Flask application
db.init_app(app)


def login_required(view):
    """
    Decorator to protect routes that require an authenticated user session.
    Redirects unauthenticated visitors to the login page.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.", "danger")
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """
    Gracefully handle CSRF token validation failures without exposing stack traces.
    """
    flash("Session security token expired or invalid. Please try submitting the form again.", "danger")
    # Redirect safely based on origin or default to login
    return redirect(request.referrer or url_for("login"))


@app.errorhandler(404)
def not_found_error(error):
    """
    Custom 404 error handler.
    """
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Custom 500 error handler to prevent stack trace leaks.
    """
    flash("An unexpected server error occurred. Please try again later.", "danger")
    return redirect(url_for("home")), 500


@app.route("/")
def home():
    """
    Home page route rendering the landing page.
    """
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles user registration:
    - GET: renders registration form.
    - POST: performs server-side validation, hashes password, and saves user to SQLite.
    """
    # Redirect already authenticated users to the dashboard
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        dob = request.form.get("dob", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []

        # 1. Validate Name
        if not name:
            errors.append("Full name is required.")
        elif len(name) < 2:
            errors.append("Name must be at least 2 characters long.")
        elif len(name) > 50:
            errors.append("Name cannot exceed 50 characters.")
        elif not re.match(r"^[a-zA-Z\s'-]+$", name):
            errors.append("Name can only contain letters, spaces, hyphens, and apostrophes.")

        # 2. Validate Email
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
        if not email:
            errors.append("Mail ID is required.")
        elif len(email) > 120:
            errors.append("Email address cannot exceed 120 characters.")
        elif not re.match(email_pattern, email):
            errors.append("Please enter a valid email address.")

        # 3. Validate Date of Birth
        if not dob:
            errors.append("Date of birth is required.")
        else:
            try:
                dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
                today = datetime.now().date()
                if dob_date > today:
                    errors.append("Date of birth cannot be in the future.")
                elif dob_date.year < 1900:
                    errors.append("Please enter a realistic year of birth (after 1900).")
            except ValueError:
                errors.append("Invalid date of birth format. Please use YYYY-MM-DD.")

        # 4. Validate Password
        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        elif len(password) > 128:
            errors.append("Password cannot exceed 128 characters.")

        # 5. Validate Password Confirmation
        if not confirm_password:
            errors.append("Please confirm your password.")
        elif password != confirm_password:
            errors.append("Passwords do not match.")

        # If any validation errors exist, display them and return to the form
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html", name=name, email=email, dob=dob)

        # 6. Database duplicate check & secure insertion
        try:
            database = db.get_db()
            existing_user = database.execute(
                "SELECT id FROM users WHERE email = ?", 
                (email,)
            ).fetchone()
            
            if existing_user:
                flash("An account with this email already exists. Please log in.", "danger")
                return render_template("register.html", name=name, email=email, dob=dob)

            # Securely hash password using Werkzeug
            password_hash = generate_password_hash(password)

            # Insert new user into SQLite database using parameterized query
            database.execute(
                "INSERT INTO users (name, email, dob, password_hash) VALUES (?, ?, ?, ?)",
                (name, email, dob, password_hash)
            )
            database.commit()

            flash("Registration successful! Please log in with your credentials.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("An account with this email already exists. Please log in.", "danger")
            return render_template("register.html", name=name, email=email, dob=dob)
        except Exception:
            flash("A database error occurred while registering your account. Please try again.", "danger")
            return render_template("register.html", name=name, email=email, dob=dob)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user authentication:
    - GET: renders the login form.
    - POST: verifies credentials, establishes Flask session, and redirects to dashboard.
    """
    # Redirect already authenticated users to the dashboard
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Invalid email or password.", "danger")
            return render_template("login.html", email=email)

        try:
            database = db.get_db()
            # Parameterized query protects against SQL injection
            user = database.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = ?", 
                (email,)
            ).fetchone()

            # Constant-time comparison / secure verification against hash
            if user is None or not check_password_hash(user["password_hash"], password):
                flash("Invalid email or password.", "danger")
                return render_template("login.html", email=email)

            # Establish new session
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))

        except Exception:
            flash("An unexpected error occurred during login. Please try again.", "danger")
            return render_template("login.html", email=email)

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """
    Protected user dashboard:
    Fetches the authenticated user profile information and displays it.
    Never exposes passwords or password hashes.
    """
    database = db.get_db()
    user = database.execute(
        "SELECT id, name, email, dob, created_at FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if user is None:
        session.clear()
        flash("User session expired or not found. Please log in again.", "danger")
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=user)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """
    Logs out the authenticated user by clearing the session.
    """
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    # Determine debug mode from environment (defaults to False for production safety)
    debug_mode = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True")
    app.run(debug=debug_mode, host="127.0.0.1", port=5000)
