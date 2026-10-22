from __future__ import annotations
"""Tests for JWTAuthenticationRules."""

import pytest
from datetime import timedelta
from flask_advanced_auth.jwt_rules import JWTAuthenticationRules
from flask_advanced_auth.exceptions import (
    InvalidDefaultKeyType,
    DefaultRuleDoesNotExist,
    InvalidJWTRule,
    JWTFieldValueError,
)


VALID_RULES = {
    "default": {
        "description": "Test default rule",
        "secret_key": "my-secret",
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=30),
        "token_header": "Bearer ",
    },
    "managers": {
        "description": "Manager tokens",
        "secret_key": "manager-secret",
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(hours=1),
        "token_header": "Bearer ",
    },
}


class TestJWTAuthenticationRulesSingleton:
    def test_singleton_returns_same_instance(self):
        r1 = JWTAuthenticationRules(rules=VALID_RULES)
        r2 = JWTAuthenticationRules()
        assert r1 is r2

    def test_singleton_reset_creates_fresh_instance(self):
        r1 = JWTAuthenticationRules(rules=VALID_RULES)
        JWTAuthenticationRules._reset()
        r2 = JWTAuthenticationRules(rules=VALID_RULES)
        # After reset, should be a new instance initialized fresh
        assert r2 is not r1 or r2.rules == VALID_RULES


class TestGetRule:
    def test_get_rule_by_name_returns_dict(self, jwt_rules):
        rule = jwt_rules.get_rule("default")
        assert isinstance(rule, dict)

    def test_get_rule_none_returns_default_rule_dict(self, jwt_rules):
        """T-06 fix: get_rule(None) must return a dict, not a string."""
        rule = jwt_rules.get_rule(None)
        assert isinstance(rule, dict), f"Expected dict, got {type(rule)}: {rule!r}"
        assert "secret_key" in rule

    def test_get_rule_named_returns_correct_rule(self):
        JWTAuthenticationRules(rules=VALID_RULES)
        rule = JWTAuthenticationRules().get_rule("managers")
        assert rule["secret_key"] == "manager-secret"

    def test_get_rule_nonexistent_returns_none(self, jwt_rules):
        rule = jwt_rules.get_rule("nonexistent")
        assert rule is None


class TestDefaultRule:
    def test_default_rule_must_exist_in_rules(self):
        with pytest.raises(DefaultRuleDoesNotExist):
            JWTAuthenticationRules(rules=VALID_RULES, default_rule="ghost")

    def test_default_rule_must_be_string(self):
        with pytest.raises(InvalidDefaultKeyType):
            JWTAuthenticationRules(rules=VALID_RULES, default_rule=123)


class TestRulesValidation:
    def test_rules_must_be_dict(self):
        with pytest.raises(TypeError):
            JWTAuthenticationRules(rules="not-a-dict")

    def test_invalid_rule_raises_invalid_jwt_rule(self):
        from flask_advanced_auth.validator import JWTRuleDetails
        bad_rules = {
            "default": {
                # missing required fields
                "algorithm": "HS256",
            }
        }
        with pytest.raises(InvalidJWTRule):
            JWTAuthenticationRules(rules=bad_rules, rule_validator=JWTRuleDetails)


class TestGetSecretKey:
    def test_get_secret_key_returns_string(self, jwt_rules):
        key = jwt_rules.get_secret_key("default")
        assert key == "test-secret-key"

    def test_get_secret_key_none_uses_default_rule(self, jwt_rules):
        key = jwt_rules.get_secret_key(None)
        assert key == "test-secret-key"

    def test_get_secret_key_missing_raises(self, jwt_rules):
        # Manually set a rule without secret_key
        jwt_rules._rules["broken"] = {"algorithm": "HS256"}
        with pytest.raises(JWTFieldValueError):
            jwt_rules.get_secret_key("broken")


class TestGetAlgorithm:
    def test_get_algorithm_returns_string(self, jwt_rules):
        algo = jwt_rules.get_algorithm("default")
        assert algo == "HS256"

    def test_get_algorithm_none_uses_default_rule(self, jwt_rules):
        algo = jwt_rules.get_algorithm(None)
        assert algo == "HS256"


class TestGetTokenHeader:
    def test_get_token_header_returns_string(self, jwt_rules):
        header = jwt_rules.get_token_header("default")
        assert header == "Bearer "

    def test_get_token_header_none_uses_default_rule(self, jwt_rules):
        header = jwt_rules.get_token_header(None)
        assert header == "Bearer "


class TestGetTokenLifetime:
    def test_get_access_lifetime(self, jwt_rules):
        lifetime = jwt_rules.get_token_lifetime("default", "access")
        assert lifetime == timedelta(minutes=30)

    def test_get_refresh_lifetime(self, jwt_rules):
        lifetime = jwt_rules.get_token_lifetime("default", "refresh")
        assert lifetime == timedelta(days=7)

    def test_missing_lifetime_raises(self, jwt_rules):
        jwt_rules._rules["norule"] = {"secret_key": "x", "algorithm": "HS256"}
        with pytest.raises(JWTFieldValueError):
            jwt_rules.get_token_lifetime("norule", "access")
