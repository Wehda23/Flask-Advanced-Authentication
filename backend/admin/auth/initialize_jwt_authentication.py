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
    """
    Initializes JWT Authentication by setting up the rules and database connection.

    Args:
        rules (dict[str, dict[str, Any]]): A dictionary of JWT rules to be validated.
        database_path (str): The import path to the SQLAlchemy database module.
        default_rule (str, optional): The key for the default JWT rule. Defaults to "default".
        rule_validator (Optional[BaseModel], optional): The validator class for the rules. Defaults to JWTRuleDetails.

    Raises:
        ImportError: If there is an error importing the database module.
        TypeError: If the provided rules or database path are invalid.
    """
    # Initiate Database
    Database(database_path)
    # Initiate JWT Rules Class
    JWTAuthenticationRules(rules, default_rule, rule_validator)
