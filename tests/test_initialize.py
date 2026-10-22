from __future__ import annotations
"""Tests for initialize_jwt_authentication."""

import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock
from flask_advanced_auth.initialize import initialize_jwt_authentication
from flask_advanced_auth.jwt_rules import JWTAuthenticationRules
from flask_advanced_auth.database import Database


RULES = {
    "default": {
        "description": "Test",
        "secret_key": "secret",
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=30),
    }
}


class TestInitializeJwtAuthentication:
    @patch("flask_advanced_auth.initialize.Database")
    @patch("flask_advanced_auth.initialize.JWTAuthenticationRules")
    def test_initializes_database_and_rules(self, mock_rules_cls, mock_db_cls):
        initialize_jwt_authentication(
            database_path="myapp.database.db",
            rules=RULES,
        )
        mock_db_cls.assert_called_once_with("myapp.database.db")
        mock_rules_cls.assert_called_once()

    @patch("flask_advanced_auth.initialize.Database")
    def test_default_rule_is_default(self, mock_db_cls):
        initialize_jwt_authentication("myapp.db", RULES)
        rules = JWTAuthenticationRules()
        assert rules.default_rule == "default"

    @patch("flask_advanced_auth.initialize.Database")
    def test_custom_default_rule(self, mock_db_cls):
        custom_rules = {
            "users": {
                "description": "User tokens",
                "secret_key": "s",
                "algorithm": "HS256",
                "access_token_lifetime": timedelta(minutes=30),
            }
        }
        initialize_jwt_authentication("myapp.db", custom_rules, default_rule="users")
        rules = JWTAuthenticationRules()
        assert rules.default_rule == "users"
