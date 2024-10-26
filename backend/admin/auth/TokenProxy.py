"""
Module contains proxy class for jwt token encoding and decoding
"""

from abc import ABC, abstractmethod
from typing import Any
import jwt
from .jwt_rules import JWTAuthenticationRules
from datetime import datetime, timezone, timedelta


class JsonWebToken(ABC):
    """
    Abstract class for jwt token encoding and decoding

    This class Implements the Proxy Design Pattern.
    """

    __rule_handler = None

    @abstractmethod
    def encode_token(
        self,
        payload: dict,
        secret_key: str,
        algorithm: str,
    ) -> str:
        pass

    @abstractmethod
    def decode_token(
        self,
        token: str,
        secret_key: str,
        algorithm: str,
    ) -> dict:
        pass


class PyJWT(JsonWebToken):
    """
    Class for jwt token encoding and decoding
    """

    __rule_handler: JWTAuthenticationRules = JWTAuthenticationRules()

    def required_payload(self, rule_name: str, token_type: str) -> dict[str, Any]:
        """
        Method that builds the required payload keys for jwt token package using JWTAuthenticationRules
        """
        token_lifetime: timedelta = self.__rule_handler.get_token_lifetime(
            rule_name, token_type
        )
        return {"type": token_type, "exp": datetime.now(timezone.utc) + token_lifetime}

    def encode_token(
        self,
        payload: dict,
        secret_key: str,
        algorithm: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        return jwt.encode(payload, key=secret_key, algorithm=algorithm, *args, **kwargs)

    def decode_token(
        self,
        token: str,
        secret_key: str,
        algorithm: str,
        *args: Any,
        **kwargs: Any,
    ) -> dict:
        """
        Decode a JWT token.

        Args:
            - token (str): The JWT token to decode

        Returns:
            - dict: The decoded token payload or None if invalid
        """
        try:
            return jwt.decode(
                token, key=secret_key, algorithms=[algorithm], *args, **kwargs
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
