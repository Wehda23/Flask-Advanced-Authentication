from __future__ import annotations
"""
Module contains the function to integrate JWT authenticator to the application.
"""

from typing import Any, Optional
from .jwt_rules import JWTAuthenticationRules
from .validator import JWTRuleDetails
from .database import Database
from pydantic import BaseModel


def initialize_jwt_authentication(
    database_path: str,
    rules: dict[str, dict[str, Any]],
    default_rule: str = "default",
    rule_validator: Optional[BaseModel] = JWTRuleDetails,
) -> None:
    """Initialize JWT Authentication by setting up the rules and database connection.

    This function must be called once at application startup (e.g. inside your
    Flask app factory) before any tokens are generated or validated.

    Args:
        database_path: Dotted import path to the Flask-SQLAlchemy ``db`` instance,
            e.g. ``"myapp.database.db"``.
        rules: Mapping of rule name → rule configuration dict.  Each dict must
            contain at minimum ``secret_key``, ``algorithm``,
            ``access_token_lifetime``, and ``description``.
        default_rule: Key of the rule that is used when no explicit rule is
            specified at call-sites.  Defaults to ``"default"``.
        rule_validator: Pydantic ``BaseModel`` subclass used to validate and
            normalise each rule dict.  Defaults to :class:`JWTRuleDetails`.

    Raises:
        ImportError: If the database module cannot be imported.
        TypeError: If ``rules`` or ``database_path`` are of an invalid type.
        InvalidJWTRule: If any rule fails Pydantic validation.
        DefaultRuleDoesNotExist: If ``default_rule`` is not a key in ``rules``.

    Example:
        >>> from datetime import timedelta
        >>> from flask_advanced_auth import initialize_jwt_authentication
        >>> initialize_jwt_authentication(
        ...     database_path="myapp.extensions.db",
        ...     rules={
        ...         "default": {
        ...             "description": "Standard user tokens",
        ...             "secret_key": "super-secret",
        ...             "algorithm": "HS256",
        ...             "access_token_lifetime": timedelta(minutes=30),
        ...             "refresh_token_lifetime": timedelta(days=7),
        ...         }
        ...     },
        ... )
    """
    # Initiate Database singleton
    Database(database_path)
    # Initiate JWT Rules singleton
    JWTAuthenticationRules(rules, default_rule, rule_validator)
