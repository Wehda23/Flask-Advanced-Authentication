from __future__ import annotations
"""
flask-advanced-auth
===================
Advanced JWT authentication for Flask with multi-rule support,
token tracking, and blacklisting.

MIT License
"""

from .initialize import initialize_jwt_authentication
from .jwt_rules import JWTAuthenticationRules
from .factory import TokenFactory
from .decorators import authenticate
from .blacklist_token import BlackListed
from .authentication_classes import (
    BaseAuthentication,
    AuthenticateJWT,
    HeaderAuthentication,
    CookieAuthentication,
    QueryParamAuthentication,
)
from .helpers import refresh_access_token, logout
from .models import AbstractTrackModelMixin, AbstractBlackListModelMixin
from .database import Database
from .exceptions import (
    InvalidDefaultKeyType,
    JWTRulesEmpty,
    DefaultRuleDoesNotExist,
    InvalidJWTRule,
    JWTFieldValueError,
    TokenExpired,
    TokenInvalid,
    TokenBlacklisted,
    TokenTypeMismatch,
)

__version__ = "0.1.0"
__author__ = "Waheed"
__license__ = "MIT"

__all__ = [
    # Core bootstrap & rules
    "initialize_jwt_authentication",
    "JWTAuthenticationRules",
    "Database",
    # Factory & Decorator
    "TokenFactory",
    "authenticate",
    "BlackListed",
    # Authentication Strategies
    "BaseAuthentication",
    "AuthenticateJWT",
    "HeaderAuthentication",
    "CookieAuthentication",
    "QueryParamAuthentication",
    # Helpers
    "refresh_access_token",
    "logout",
    # Model Mixins
    "AbstractTrackModelMixin",
    "AbstractBlackListModelMixin",
    # Exceptions
    "InvalidDefaultKeyType",
    "JWTRulesEmpty",
    "DefaultRuleDoesNotExist",
    "InvalidJWTRule",
    "JWTFieldValueError",
    "TokenExpired",
    "TokenInvalid",
    "TokenBlacklisted",
    "TokenTypeMismatch",
]
