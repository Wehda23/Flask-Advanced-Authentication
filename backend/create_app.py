"""
Module contains function to create flask application
"""

from flask import Flask
from typing import Any
from backend.config import config_modes


def create_app(mode: str = "production", *args: Any, **kwargs: Any) -> Flask:
    """
    Creates a Flask application.

    :param mode: The mode of the application, e.g., 'development', 'testing', 'production'.
    :param args: Additional positional arguments.
    :param kwargs: Additional keyword arguments to pass to the Flask constructor.
    :return: A configured Flask application.
    """
    # Create Flask Application
    app: Flask = Flask(__name__, **kwargs)

    # Handle Flask Configurations
    config_class = config_modes.get(mode)
    if not config_class:
        raise ValueError(f"Unknown mode: {mode}")
    app.config.from_object(config_class)

    # Return Flask Application
    return app
