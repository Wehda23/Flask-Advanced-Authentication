from __future__ import annotations
"""Tests for authentication_classes — BaseAuthentication and AuthenticateJWT."""

import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_advanced_auth.authentication_classes import AuthenticateJWT, BaseAuthentication
from flask_advanced_auth.factory import TokenFactory


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_request(auth_header: str = None) -> MagicMock:
    """Create a mock Flask request with the given Authorization header."""
    req = MagicMock()
    req.headers = {"Authorization": auth_header} if auth_header else {}
    return req


# ── parse_token tests (T-03 fix verification) ─────────────────────────────────

class TestParseToken:
    def setup_method(self):
        self.auth = AuthenticateJWT("Bearer ", "access", "default")

    def test_parse_valid_bearer_token(self):
        req = make_request("Bearer mytoken123")
        token = self.auth.parse_token(req)
        assert token == "mytoken123"

    def test_parse_missing_header_returns_none(self):
        req = make_request(None)
        token = self.auth.parse_token(req)
        assert token is None

    def test_parse_wrong_prefix_returns_none(self):
        req = make_request("Token mytoken123")
        token = self.auth.parse_token(req)
        assert token is None

    def test_parse_empty_token_after_prefix_returns_none(self):
        req = make_request("Bearer ")
        token = self.auth.parse_token(req)
        assert token is None

    def test_parse_custom_prefix(self):
        auth = AuthenticateJWT("Token ", "access", "default")
        req = make_request("Token abc.def.ghi")
        assert auth.parse_token(req) == "abc.def.ghi"


# ── AuthenticateJWT.authenticate tests ───────────────────────────────────────

class TestAuthenticateJWT:
    def test_authenticate_valid_token_returns_payload(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")
        auth = AuthenticateJWT("Bearer ", "access", "default")
        payload = auth.authenticate(token)
        assert payload is not None
        assert payload["type"] == "access"

    def test_authenticate_invalid_token_returns_none(self, jwt_rules):
        auth = AuthenticateJWT("Bearer ", "access", "default")
        payload = auth.authenticate("not.a.valid.token")
        assert payload is None

    def test_authenticate_wrong_type_returns_none(self, jwt_rules):
        factory = TokenFactory()
        # Can only test this if refresh lifetime is configured — it is in DEFAULT_RULES
        token = factory.generate_token(rule_name="default")
        # Try to authenticate an access token as refresh
        auth = AuthenticateJWT("Bearer ", "refresh", "default")
        payload = auth.authenticate(token)
        assert payload is None

    @patch("flask_advanced_auth.authentication_classes.BlackListed")
    def test_authenticate_blacklisted_token_returns_none(self, mock_bl_class, jwt_rules):
        mock_bl = MagicMock()
        mock_bl.is_blacklisted.return_value = True
        mock_bl_class.return_value = mock_bl

        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")
        auth = AuthenticateJWT("Bearer ", "access", "default")
        payload = auth.authenticate(token)
        assert payload is None


# ── authenticate_request end-to-end ──────────────────────────────────────────

class TestAuthenticateRequest:
    def test_full_flow_valid_request(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")

        req = make_request(f"Bearer {token}")
        auth = AuthenticateJWT("Bearer ", "access", "default")
        payload = auth.authenticate_request(req)
        assert payload is not None
        assert payload["type"] == "access"

    def test_full_flow_missing_header(self, jwt_rules):
        req = make_request(None)
        auth = AuthenticateJWT("Bearer ", "access", "default")
        payload = auth.authenticate_request(req)
        assert payload is None


from flask_advanced_auth.authentication_classes import (
    HeaderAuthentication,
    CookieAuthentication,
    QueryParamAuthentication,
)


class TestCookieAuthentication:
    def test_cookie_auth_extracts_token(self):
        auth = CookieAuthentication(cookie_name="my_jwt")
        req = MagicMock()
        req.cookies = {"my_jwt": "cookie-token-123"}
        assert auth.parse_token(req) == "cookie-token-123"

    def test_cookie_auth_missing_cookie_returns_none(self):
        auth = CookieAuthentication(cookie_name="my_jwt")
        req = MagicMock()
        req.cookies = {}
        assert auth.parse_token(req) is None


class TestQueryParamAuthentication:
    def test_query_param_auth_extracts_token(self):
        auth = QueryParamAuthentication(param_name="api_token")
        req = MagicMock()
        req.args = {"api_token": "query-token-456"}
        assert auth.parse_token(req) == "query-token-456"

    def test_query_param_auth_missing_returns_none(self):
        auth = QueryParamAuthentication(param_name="api_token")
        req = MagicMock()
        req.args = {}
        assert auth.parse_token(req) is None


class TestHeaderAuthentication:
    def test_header_auth_is_subclass(self):
        assert issubclass(HeaderAuthentication, AuthenticateJWT)
