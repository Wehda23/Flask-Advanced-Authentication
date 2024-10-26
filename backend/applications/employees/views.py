"""
Module contains employees api views
"""

from flask import Response, make_response
from .route import employees_api


@employees_api.route("")
def employees() -> Response:
    """
    Employees api view
    """
    return make_response({"test": 12, "Working": True, "API": "Employees"}, 200)
