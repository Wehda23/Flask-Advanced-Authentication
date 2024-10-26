"""
Module contains function that register all Flask BluePrints to flask application
"""

from flask import Flask
from backend.applications import users_api, managers_api, employees_api


# Function To register flask blueprints to flask application
def register_routes(app: Flask) -> None:
    """
    Register all blueprints to flask application

    Args:
        app (Flask): Flask application
    """
    # Register Routes
    app.register_blueprint(users_api)
    app.register_blueprint(managers_api)
    app.register_blueprint(employees_api)
