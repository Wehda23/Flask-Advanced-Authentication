"""
Module contains base authentication classes
"""

from abc import ABC, abstractmethod
from typing import Any, Union
from flask import Request
from .blacklist_token import BlackListed
from .factory import TokenFactory


class BaseAuthentication(ABC):
    """Base class for authentication methods"""

    def __init__(
        self,
        token_headers: str,
        token_type: str,
        rule_name: str,
    ) -> None:
        """Initializes the authentication class
        Args:
        secret_key (str): Secret key for token generation
        algorithm (str): Algorithm used for token generation
        token_headers (str): Headers for token generation
        """
        self.token_headers: str = token_headers
        self.token_type: str = token_type
        self.rule_name: str = rule_name

    def parse_token(self, request: Request) -> Any:
        """Parse the JWT token from the request headers or query parameters"""
        pass

    @abstractmethod
    def authenticate(self, token: str) -> dict[str, Any]:
        """Authenticate the user based on the request."""
        pass

    def authenticate_request(
        self,
        request: Request,
    ) -> Any:
        """
        Authenticate the request using the JWT token.

        Args:
            request (Request): The request object
            assign_to_request (bool): Whether to assign the authenticated user to the request object. Defaults to\
            False.
            assigment_key (str): The key to assign the authenticated user to the request object.
        """
        token = self.parse_token(request)
        payload: dict[str, Any] = self.authenticate(token)
        return payload


class AuthenticateJWT(BaseAuthentication):
    """Class for JWT authentication"""

    def validate_token(self, token: str) -> Union[dict[str, Any], None]:
        """Validate the JWT token"""
        try:
            return TokenFactory().validate_token(token, self.rule_name)
        except Exception as e:
            return None

    def validate_token_type(self, decoded_payload: dict[str, Any]) -> bool:
        """Validate the token type"""
        return decoded_payload.get("type") == self.token_type

    def authenticate(self, token: str) -> dict[str, Any]:
        """
        Authenticate the token based on the JWT token rules.
        """
        # Implement JWT token validation here
        # Check if token is blacklisted
        if BlackListed().is_blacklisted(self.rule_name, token):
            return None

        # Decode the token
        payload: Union[dict[str, Any], None] = self.validate_token(token)
        if payload is None:
            return None

        # Validate the token type
        if not self.validate_token_type(payload):
            return None

        return payload
