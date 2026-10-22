from __future__ import annotations
"""Tests for the JWTRuleDetails Pydantic validator."""

import pytest
from datetime import timedelta
from pydantic import ValidationError
from flask_advanced_auth.validator import JWTRuleDetails, check_validator_class
from pydantic import BaseModel


VALID_RULE = {
    "description": "Test rule",
    "secret_key": "my-secret",
    "algorithm": "HS256",
    "access_token_lifetime": timedelta(minutes=30),
}


class TestJWTRuleDetails:
    def test_valid_minimal_rule_passes(self):
        rule = JWTRuleDetails(**VALID_RULE)
        assert rule.secret_key == "my-secret"
        assert rule.algorithm == "HS256"

    def test_access_expires_in_set_from_access_token_lifetime(self):
        rule = JWTRuleDetails(**VALID_RULE)
        assert rule.access_expires_in == timedelta(minutes=30)

    def test_refresh_expires_in_defaults_to_none(self):
        rule = JWTRuleDetails(**VALID_RULE)
        assert rule.refresh_expires_in is None

    def test_table_defaults_to_false(self):
        """T-02 fix: 'table' alias must be 'table', not 'tabel'."""
        rule = JWTRuleDetails(**{**VALID_RULE, "table": True})
        assert rule.table is True

    def test_table_path_alias(self):
        """T-02 fix: 'table_path' alias must be 'table_path', not 'tabel_path'."""
        rule = JWTRuleDetails(**{**VALID_RULE, "table_path": "myapp.models.User"})
        assert rule.table_path == "myapp.models.User"

    def test_TABLE_alias_works(self):
        """Uppercase alias 'TABLE' should also work."""
        rule = JWTRuleDetails(**{**VALID_RULE, "TABLE": True})
        assert rule.table is True

    def test_TABLE_PATH_alias_works(self):
        rule = JWTRuleDetails(**{**VALID_RULE, "TABLE_PATH": "myapp.models.User"})
        assert rule.table_path == "myapp.models.User"

    def test_token_header_defaults_to_bearer(self):
        rule = JWTRuleDetails(**VALID_RULE)
        assert rule.token_header == "Bearer "

    def test_blank_token_header_raises(self):
        with pytest.raises(ValidationError):
            JWTRuleDetails(**{**VALID_RULE, "token_header": "   "})

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            JWTRuleDetails(
                description="Test",
                algorithm="HS256",
                # missing secret_key and access_token_lifetime
            )

    def test_blacklisted_defaults_to_false(self):
        rule = JWTRuleDetails(**VALID_RULE)
        assert rule.blacklisted is False

    def test_track_created_defaults_to_false(self):
        rule = JWTRuleDetails(**VALID_RULE)
        assert rule.track_created is False

    def test_track_created_allow_duplicates_defaults_to_true(self):
        rule = JWTRuleDetails(**VALID_RULE)
        assert rule.track_created_allow_duplicates is True

    def test_model_dump_includes_all_fields(self):
        rule = JWTRuleDetails(**VALID_RULE)
        dumped = rule.model_dump()
        assert "secret_key" in dumped
        assert "algorithm" in dumped
        assert "access_expires_in" in dumped


class TestCheckValidatorClass:
    def test_returns_true_for_base_model_subclass(self):
        class MyModel(BaseModel):
            name: str

        assert check_validator_class(MyModel) is True

    def test_returns_false_for_non_base_model(self):
        class NotAModel:
            pass

        assert check_validator_class(NotAModel) is False

    def test_returns_false_for_non_class(self):
        assert check_validator_class("not-a-class") is False
