from __future__ import annotations
"""
Module contains proxy class for JWT token encoding and decoding.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import jwt
from .jwt_rules import JWTAuthenticationRules
from datetime import datetime, timezone, timedelta


class JsonWebToken(ABC):
    """Abstract base class for JWT encode/decode operations (Proxy pattern)."""

    @abstractmethod
    def encode_token(self, payload: dict, secret_key: str, algorithm: str) -> str:
        """Encode a payload into a JWT token string."""
        pass

    @abstractmethod
    def decode_token(self, token: str, secret_key: str, algorithm: str) -> Optional[dict]:
        """Decode a JWT token string into a payload dict."""
        pass


class PyJWT(JsonWebToken):
    """Concrete JWT proxy using the PyJWT library."""

    @property
    def rule_handler(self) -> JWTAuthenticationRules:
        return JWTAuthenticationRules()

    def required_payload(self, rule_name: str, token_type: str) -> dict[str, Any]:
        """Build the standard required payload fields (type + expiry)."""
        token_lifetime: timedelta = self.rule_handler.get_token_lifetime(
            rule_name, token_type
        )
        return {
            "type": token_type,
            "exp": datetime.now(timezone.utc) + token_lifetime,
        }

    def encode_token(
        self,
        payload: dict,
        secret_key: str,
        algorithm: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Encode a payload dict into a signed JWT string."""
        return jwt.encode(payload, key=secret_key, algorithm=algorithm, *args, **kwargs)

    def decode_token(
        self,
        token: str,
        secret_key: str,
        algorithm: str,
        *args: Any,
        **kwargs: Any,
    ) -> Optional[dict]:
        """Decode and verify a JWT token."""
        try:
            return jwt.decode(
                token, key=secret_key, algorithms=[algorithm], *args, **kwargs
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
