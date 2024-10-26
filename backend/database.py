"""
Module contails function to initialize database models and app database configurations
"""

from flask import Flask
from backend.models import db


# Function to handle database intiliaztion
def database_init(app: Flask) -> None:
    """
    Function to handle database intiliaztion

    Args:
        app (Flask): Flask app instance
    """
    # Initialize the app with the extension
    db.init_app(app)

    # Create Database Tables
    with app.app_context():
        db.create_all()

    # Clear Session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """
        Closes session after each request or application context shutdown to avoid leaks
        """
        db.session.remove()
