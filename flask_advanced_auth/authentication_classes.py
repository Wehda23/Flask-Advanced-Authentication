from __future__ import annotations
"""
Module contains base and concrete authentication classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from flask import Request
from .blacklist_token import BlackListed
from .factory import TokenFactory


class BaseAuthentication(ABC):
    """Abstract base class for authentication strategies.

    Subclass this to implement custom token extraction and validation logic.

    Args:
        token_headers: The prefix expected in the Authorization header (e.g. 'Bearer ').
        token_type: The expected token type field value (e.g. 'access', 'refresh').
        rule_name: The JWT rule name to use for validation.
    """

    def __init__(
        self,
        token_headers: str = "Bearer ",
        token_type: str = "access",
        rule_name: Optional[str] = None,
    ) -> None:
        self.token_headers: str = token_headers
        self.token_type: str = token_type
        self.rule_name: Optional[str] = rule_name

    def parse_token(self, request: Request) -> Optional[str]:
        """Extract the JWT string from the request Authorization header.

        Expects the header format: ``Authorization: <prefix><token>``
        where ``prefix`` is ``self.token_headers`` (e.g. ``'Bearer '``).
        """
        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header:
            return None
        if not auth_header.startswith(self.token_headers):
            return None
        token = auth_header[len(self.token_headers):]
        if not token:
            return None
        return token

    @abstractmethod
    def authenticate(self, token: str) -> Optional[dict[str, Any]]:
        """Validate a token and return its payload, or None if invalid."""
        pass

    def authenticate_request(self, request: Request) -> Optional[dict[str, Any]]:
        """Extract and authenticate the token from the request.

        Args:
            request: The Flask request object.

        Returns:
            The decoded token payload dict if valid, None otherwise.
        """
        token = self.parse_token(request)
        if token is None:
            return None
        return self.authenticate(token)


class AuthenticateJWT(BaseAuthentication):
    """Standard JWT authentication — validates token extracted from Authorization header.

    Checks:
    1. Token is not blacklisted (if blacklisting is enabled for the rule).
    2. Token signature and expiry are valid.
    3. Token type matches the expected type.
    """

    def validate_token(self, token: str) -> Optional[dict[str, Any]]:
        """Decode and verify a token using the configured rule."""
        try:
            return TokenFactory().validate_token(token, self.rule_name)
        except Exception:
            return None

    def validate_token_type(self, decoded_payload: dict[str, Any]) -> bool:
        """Check that the decoded payload's 'type' field matches self.token_type."""
        return decoded_payload.get("type") == self.token_type

    def authenticate(self, token: str) -> Optional[dict[str, Any]]:
        """Validate a JWT token string.

        Args:
            token: The raw JWT string.

        Returns:
            The decoded payload if all checks pass, None otherwise.
        """
        if BlackListed().is_blacklisted(self.rule_name, token):
            return None

        payload: Optional[dict[str, Any]] = self.validate_token(token)
        if payload is None:
            return None

        if not self.validate_token_type(payload):
            return None

        return payload


class HeaderAuthentication(AuthenticateJWT):
    """Explicit alias for Header-based JWT authentication."""
    pass


class CookieAuthentication(AuthenticateJWT):
    """JWT authentication that extracts tokens from HTTP cookies.

    Args:
        token_headers: Unused (kept for interface compatibility).
        token_type: Expected token type ('access' or 'refresh').
        rule_name: JWT rule name.
        cookie_name: Name of the cookie containing the token (default: 'access_token').
    """

    cookie_name: str = "access_token"

    def __init__(
        self,
        token_headers: str = "Bearer ",
        token_type: str = "access",
        rule_name: Optional[str] = None,
        cookie_name: str = "access_token",
    ) -> None:
        super().__init__(token_headers=token_headers, token_type=token_type, rule_name=rule_name)
        self.cookie_name = cookie_name

    def parse_token(self, request: Request) -> Optional[str]:
        """Extract the token from request cookies."""
        return request.cookies.get(self.cookie_name)


class QueryParamAuthentication(AuthenticateJWT):
    """JWT authentication that extracts tokens from URL query parameters.

    Args:
        token_headers: Unused (kept for interface compatibility).
        token_type: Expected token type ('access' or 'refresh').
        rule_name: JWT rule name.
        param_name: Name of the query parameter (default: 'token').
    """

    param_name: str = "token"

    def __init__(
        self,
        token_headers: str = "Bearer ",
        token_type: str = "access",
        rule_name: Optional[str] = None,
        param_name: str = "token",
    ) -> None:
        super().__init__(token_headers=token_headers, token_type=token_type, rule_name=rule_name)
        self.param_name = param_name

    def parse_token(self, request: Request) -> Optional[str]:
        """Extract the token from query arguments."""
        return request.args.get(self.param_name)
