"""
app.py - Main entry point for the Flask application.
"""
import os
from flask import Flask, render_template, request, flash, redirect, url_for
from database import db

# Initialize the Flask application
app = Flask(__name__)

# Basic configuration
# Secret key is needed for session management and flash messages (will be used in auth)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Register database helpers and CLI commands with the Flask application
db.init_app(app)


@app.route("/")
def home():
    """
    Home page route rendering the initial landing page.
    """
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Placeholder registration route.
    Handles GET to display the frontend registration form,
    and POST to handle placeholder submission without saving data.
    """
    if request.method == "POST":
        # Placeholder response - no database storage or authentication logic implemented yet
        flash("Frontend validation passed! Placeholder submission received (no data was stored).", "success")
        return redirect(url_for("register"))

    return render_template("register.html")


if __name__ == "__main__":
    # Run the development server
    app.run(debug=True, host="127.0.0.1", port=5000)
