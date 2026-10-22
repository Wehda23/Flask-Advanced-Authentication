from __future__ import annotations
"""
Module contains exceptions for flask-advanced-auth package.
"""


class InvalidDefaultKeyType(Exception):
    """Raised when the default rule key is not a string."""

    def __str__(self) -> str:
        return f"InvalidDefaultKeyType: {super().__str__()}"


class JWTRulesEmpty(Exception):
    """Raised when JWT rules have not been configured."""

    def __str__(self) -> str:
        return f"JWTRulesEmpty: {super().__str__()}"


class DefaultRuleDoesNotExist(Exception):
    """Raised when the specified default rule key is not found in the rules dict."""

    def __str__(self) -> str:
        return f"DefaultRuleDoesNotExist: {super().__str__()}"


class InvalidJWTRule(Exception):
    """Raised when a JWT rule fails Pydantic validation."""

    def __str__(self) -> str:
        return f"InvalidJWTRule: {super().__str__()}"


class JWTFieldValueError(Exception):
    """Raised when a required JWT rule field is None or missing."""

    def __str__(self) -> str:
        return f"JWTFieldValueError: {super().__str__()}"


class TokenExpired(Exception):
    """Raised when a JWT token has expired."""

    def __str__(self) -> str:
        return f"TokenExpired: {super().__str__()}"


class TokenInvalid(Exception):
    """Raised when a JWT token is invalid."""

    def __str__(self) -> str:
        return f"TokenInvalid: {super().__str__()}"


class TokenBlacklisted(Exception):
    """Raised when a JWT token has been blacklisted."""

    def __str__(self) -> str:
        return f"TokenBlacklisted: {super().__str__()}"


class TokenTypeMismatch(Exception):
    """Raised when a JWT token type does not match the expected type."""

    def __str__(self) -> str:
        return f"TokenTypeMismatch: {super().__str__()}"
