"""
app.py - Main entry point for the Flask application.
"""
import os
from flask import Flask, render_template

# Initialize the Flask application
app = Flask(__name__)

# Basic configuration
# Secret key is needed for session management and flash messages (will be used in auth)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")


@app.route("/")
def home():
    """
    Home page route rendering the initial landing page.
    """
    return render_template("index.html")


if __name__ == "__main__":
    # Run the development server
    app.run(debug=True, host="127.0.0.1", port=5000)
