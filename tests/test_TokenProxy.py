from __future__ import annotations
"""Tests for PyJWT token proxy."""

import pytest
from datetime import timedelta, datetime, timezone
from flask_advanced_auth.TokenProxy import PyJWT
import jwt as pyjwt_lib


SECRET = "test-secret"
ALGORITHM = "HS256"


@pytest.fixture
def proxy(jwt_rules):
    """PyJWT proxy instance (requires rules to be initialized for required_payload)."""
    return PyJWT()


class TestEncodeDecodeRoundTrip:
    def test_encode_returns_string(self, proxy):
        payload = {"user": 1, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        token = proxy.encode_token(payload, SECRET, ALGORITHM)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_returns_payload(self, proxy):
        payload = {"user": 1, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        token = proxy.encode_token(payload, SECRET, ALGORITHM)
        decoded = proxy.decode_token(token, SECRET, ALGORITHM)
        assert decoded is not None
        assert decoded["user"] == 1

    def test_decode_wrong_secret_returns_none(self, proxy):
        payload = {"user": 1, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        token = proxy.encode_token(payload, SECRET, ALGORITHM)
        decoded = proxy.decode_token(token, "wrong-secret", ALGORITHM)
        assert decoded is None

    def test_decode_expired_token_returns_none(self, proxy):
        payload = {"user": 1, "exp": datetime.now(timezone.utc) - timedelta(seconds=1)}
        token = proxy.encode_token(payload, SECRET, ALGORITHM)
        decoded = proxy.decode_token(token, SECRET, ALGORITHM)
        assert decoded is None

    def test_decode_tampered_token_returns_none(self, proxy):
        payload = {"user": 1, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        token = proxy.encode_token(payload, SECRET, ALGORITHM)
        tampered = token[:-5] + "XXXXX"
        decoded = proxy.decode_token(tampered, SECRET, ALGORITHM)
        assert decoded is None


class TestRequiredPayload:
    def test_required_payload_access_has_type_and_exp(self, proxy, jwt_rules):
        result = proxy.required_payload("default", "access")
        assert result["type"] == "access"
        assert "exp" in result
        # exp should be roughly now + 30min
        now = datetime.now(timezone.utc)
        delta = result["exp"] - now
        assert timedelta(minutes=28) < delta < timedelta(minutes=32)

    def test_required_payload_refresh_has_type_and_exp(self, proxy, jwt_rules):
        result = proxy.required_payload("default", "refresh")
        assert result["type"] == "refresh"
        assert "exp" in result
        now = datetime.now(timezone.utc)
        delta = result["exp"] - now
        assert timedelta(days=6, hours=23) < delta < timedelta(days=7, hours=1)
