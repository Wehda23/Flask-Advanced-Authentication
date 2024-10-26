"""
Module contains managers api views
"""

from flask import Response, make_response
from ..route import managers_api


@managers_api.route("")
def managers() -> Response:
    """
    managers api view
    """
    return make_response({"test": 12, "Working": True, "API": "Managers"}, 200)
