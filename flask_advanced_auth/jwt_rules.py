from __future__ import annotations
"""
Module that contains JWTAuthenticationRules — the central rule registry.
"""

from typing import Any, Type, Optional, NoReturn, Union
from .exceptions import (
    InvalidDefaultKeyType,
    JWTRulesEmpty,
    DefaultRuleDoesNotExist,
    InvalidJWTRule,
    JWTFieldValueError,
)
from pydantic import ValidationError, BaseModel
from .validator import check_validator_class


class JWTAuthenticationRules:
    """Singleton registry for JWT authentication rules.

    Initialized once via :func:`initialize_jwt_authentication`, then
    accessible anywhere as ``JWTAuthenticationRules()``.
    """

    _instance: Optional[JWTAuthenticationRules] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> JWTAuthenticationRules:
        if cls._instance is None:
            cls._instance = super(JWTAuthenticationRules, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        rules: Optional[dict[str, dict[str, Any]]] = None,
        default_rule: str = "default",
        rule_validator: Optional[BaseModel] = None,
    ) -> None:
        if rules is not None:
            self.rule_validator = rule_validator
            self.rules = rules
            self.default_rule = default_rule
            self._initialized = True

    @classmethod
    def _reset(cls) -> None:
        """Reset singleton state. Intended for use in tests only."""
        if cls._instance is not None:
            if hasattr(cls._instance, "_rules"):
                del cls._instance._rules
            if hasattr(cls._instance, "_default_rule"):
                del cls._instance._default_rule
            if hasattr(cls._instance, "_rule_validator"):
                del cls._instance._rule_validator
            if hasattr(cls._instance, "_initialized"):
                del cls._instance._initialized
        cls._instance = None

    @property
    def rule_validator(self) -> Optional[Type[BaseModel]]:
        """The Pydantic validator class used to validate each rule dict."""
        return getattr(self, "_rule_validator", None)

    @rule_validator.setter
    def rule_validator(self, value: Optional[BaseModel]) -> None:
        if value is not None and not check_validator_class(value):
            raise TypeError("rule_validator must be a subclass of Pydantic BaseModel")
        self._rule_validator: Optional[BaseModel] = value

    @property
    def rules(self) -> dict[str, dict[str, Any]]:
        """The registered JWT rules dictionary."""
        if not hasattr(self, "_rules"):
            raise JWTRulesEmpty("JWT rules have not been configured. Call initialize_jwt_authentication() first.")
        return self._rules

    @rules.setter
    def rules(self, value: dict[str, dict[str, Any]]) -> None:
        if not isinstance(value, dict):
            raise TypeError(f"rules must be a dictionary, not {type(value)}")
        if self.rule_validator:
            self._rules = self.validate_rules(value)
            return
        self._rules = value

    def validate_rules(
        self, rules: dict[str, dict[str, Any]]
    ) -> Union[dict[str, dict[str, Any]], NoReturn]:
        """Validate each rule dict against the Pydantic rule_validator."""
        errors: dict[str, list[dict[str, Any]]] = {}
        updated_rules: dict[str, dict[str, Any]] = {}

        for key, rule in rules.items():
            if not isinstance(rule, dict):
                raise TypeError(f"rule '{key}' must be a dictionary, not {type(rule)}")
            try:
                rule_validator = self.rule_validator(**rule)
                updated_rules[key] = rule_validator.model_dump()
            except ValidationError as e:
                errors[key] = e.errors()

        if errors:
            raise InvalidJWTRule(errors)

        return updated_rules

    @property
    def default_rule(self) -> str:
        """The name of the default rule."""
        if not hasattr(self, "_default_rule"):
            return "default"
        return self._default_rule

    @default_rule.setter
    def default_rule(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidDefaultKeyType(
                f"Default rule key must be a string, got {type(value)}"
            )
        if not hasattr(self, "_rules"):
            raise JWTRulesEmpty("Rules must be set before setting default_rule")
        if value not in self.rules:
            raise DefaultRuleDoesNotExist(
                f"Default rule '{value}' does not exist in JWT_AUTHENTICATION_RULES."
            )
        self._default_rule = value

    def get_rule(self, rule: Optional[str] = None, *args: Any, **kwargs: Any) -> Optional[dict[str, Any]]:
        """Retrieve a JWT rule dict by name."""
        if rule is None:
            return self.rules.get(self.default_rule)
        return self.rules.get(rule, *args, **kwargs)

    @staticmethod
    def disallow_none(value: Any, error_message: str, *args: Any, **kwargs: Any) -> Any:
        """Assert a value is not None, raising JWTFieldValueError if it is."""
        if value is None:
            raise JWTFieldValueError(error_message)
        return value

    def get_secret_key(self, rule_name: Optional[str] = None, key_name: str = "secret_key") -> str:
        """Get the secret key for a rule."""
        if rule_name is None:
            rule_name = self.default_rule
        rule = self.get_rule(rule_name)
        return self.disallow_none(
            rule.get(key_name) if rule else None,
            f"Secret key for rule '{rule_name}' is not defined. "
            f"Add 'secret_key' to your JWT_AUTHENTICATION_RULES['{rule_name}'].",
        )

    def get_algorithm(self, rule_name: Optional[str] = None, key_name: str = "algorithm") -> str:
        """Get the algorithm for a rule."""
        if rule_name is None:
            rule_name = self.default_rule
        rule = self.get_rule(rule_name)
        return self.disallow_none(
            rule.get(key_name) if rule else None,
            f"Algorithm for rule '{rule_name}' is not defined. "
            f"Add 'algorithm' to your JWT_AUTHENTICATION_RULES['{rule_name}'].",
        )

    def get_token_lifetime(self, rule_name: Optional[str] = None, token_type: str = "access") -> Any:
        """Get the token lifetime timedelta for a given token type."""
        if rule_name is None:
            rule_name = self.default_rule
        rule = self.get_rule(rule_name)
        lifetime = None
        if rule:
            lifetime = rule.get(f"{token_type}_expires_in")
            if lifetime is None:
                lifetime = rule.get(f"{token_type}_token_lifetime")
        return self.disallow_none(
            lifetime,
            f"Token lifetime for '{token_type}' token is not defined in rule '{rule_name}'. "
            f"Add '{token_type}_token_lifetime' (a timedelta) to your rule.",
        )

    def get_access_lifetime(self, rule_name: Optional[str] = None) -> Any:
        """Get the access token lifetime for a rule."""
        return self.get_token_lifetime(rule_name, "access")

    def get_refresh_lifetime(self, rule_name: Optional[str] = None) -> Any:
        """Get the refresh token lifetime for a rule."""
        return self.get_token_lifetime(rule_name, "refresh")

    def get_table(self, rule_name: Optional[str] = None, key_name: str = "table") -> bool:
        """Check if the rule is associated with a database table."""
        rule = self.get_rule(rule_name)
        return bool(rule.get(key_name, False)) if rule else False

    def get_table_path(self, rule_name: Optional[str] = None, key_name: str = "table_path") -> str:
        """Get the model import path for a rule."""
        if rule_name is None:
            rule_name = self.default_rule
        rule = self.get_rule(rule_name)
        return self.disallow_none(
            rule.get(key_name) if rule else None,
            f"Rule '{rule_name}' has 'table=True' but no 'table_path' defined. "
            f"Add 'table_path': 'myapp.models.MyModel' to your rule.",
        )

    def get_token_header(self, rule_name: Optional[str] = None, key_name: str = "token_header") -> str:
        """Get the token header prefix for a rule (e.g. 'Bearer ')."""
        if rule_name is None:
            rule_name = self.default_rule
        rule = self.get_rule(rule_name)
        return self.disallow_none(
            rule.get(key_name) if rule else None,
            f"Rule '{rule_name}' does not have a 'token_header' defined. "
            f"Add 'token_header': 'Bearer ' to your rule.",
        )

    def get_track_created(self, rule_name: Optional[str] = None, key_name: str = "track_created") -> bool:
        """Check if the rule enables token tracking."""
        rule = self.get_rule(rule_name)
        return bool(rule.get(key_name, False)) if rule else False

    def get_track_created_table_path(
        self, rule_name: Optional[str] = None, key_name: str = "track_created_table_path"
    ) -> str:
        """Get the track model import path for a rule."""
        if rule_name is None:
            rule_name = self.default_rule
        rule = self.get_rule(rule_name)
        return self.disallow_none(
            rule.get(key_name) if rule else None,
            f"Rule '{rule_name}' has 'track_created=True' but no 'track_created_table_path' defined. "
            f"Add 'track_created_table_path': 'myapp.models.TrackModel' to your rule.",
        )

    def get_track_created_allow_duplicates(
        self, rule_name: Optional[str] = None, key_name: str = "track_created_allow_duplicates"
    ) -> bool:
        """Check whether duplicate tracked tokens are allowed for a rule."""
        rule = self.get_rule(rule_name)
        return bool(rule.get(key_name, True)) if rule else True

    def get_blacklisted(self, rule_name: Optional[str] = None, key_name: str = "blacklisted") -> bool:
        """Check if blacklisting is enabled for a rule."""
        rule = self.get_rule(rule_name)
        return bool(rule.get(key_name, False)) if rule else False

    def get_blacklisted_table_path(
        self, rule_name: Optional[str] = None, key_name: str = "blacklisted_table_path"
    ) -> str:
        """Get the blacklist model import path for a rule."""
        if rule_name is None:
            rule_name = self.default_rule
        rule = self.get_rule(rule_name)
        return self.disallow_none(
            rule.get(key_name) if rule else None,
            f"Rule '{rule_name}' has 'blacklisted=True' but no 'blacklisted_table_path' defined. "
            f"Add 'blacklisted_table_path': 'myapp.models.BlacklistedToken' to your rule.",
        )
