from __future__ import annotations
"""
Compatibility layer for the demo backend.
Re-exports from the standalone flask_advanced_auth package.
"""

from flask_advanced_auth import (
    initialize_jwt_authentication,
    JWTAuthenticationRules,
    Database,
)
from flask_advanced_auth.import_handler import import_handler

__all__ = [
    "initialize_jwt_authentication",
    "JWTAuthenticationRules",
    "Database",
    "import_handler",
]
