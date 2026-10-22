from __future__ import annotations
"""Tests for convenience helpers — refresh_access_token and logout."""

import pytest
from unittest.mock import MagicMock, patch
from flask_advanced_auth.helpers import refresh_access_token, logout
from flask_advanced_auth.factory import TokenFactory
from flask_advanced_auth.exceptions import TokenInvalid, TokenBlacklisted, TokenTypeMismatch


class TestRefreshAccessToken:
    def test_refresh_valid_token_issues_new_access_token(self, jwt_rules):
        factory = TokenFactory()
        refresh_token = factory.generate_refresh_token(rule_name="default")

        new_access_token = refresh_access_token(refresh_token, rule_name="default")
        assert isinstance(new_access_token, str)

        payload = factory.validate_token(new_access_token, rule_name="default")
        assert payload is not None
        assert payload["type"] == "access"

    def test_refresh_with_invalid_token_raises_token_invalid(self, jwt_rules):
        with pytest.raises(TokenInvalid):
            refresh_access_token("completely.invalid.token", rule_name="default")

    def test_refresh_with_access_token_raises_type_mismatch(self, jwt_rules):
        factory = TokenFactory()
        access_token = factory.generate_token(rule_name="default")

        with pytest.raises(TokenTypeMismatch):
            refresh_access_token(access_token, rule_name="default")

    @patch("flask_advanced_auth.helpers.BlackListed")
    def test_refresh_with_blacklisted_token_raises_token_blacklisted(self, mock_bl_class, jwt_rules):
        mock_bl = MagicMock()
        mock_bl.is_blacklisted.return_value = True
        mock_bl_class.return_value = mock_bl

        factory = TokenFactory()
        refresh_token = factory.generate_refresh_token(rule_name="default")

        with pytest.raises(TokenBlacklisted):
            refresh_access_token(refresh_token, rule_name="default")


class TestLogout:
    @patch("flask_advanced_auth.helpers.BlackListed")
    def test_logout_calls_blacklist(self, mock_bl_class):
        mock_bl = MagicMock()
        mock_bl_class.return_value = mock_bl

        logout("some.token", rule_name="default", remove_from_track=True)
        mock_bl.blacklist.assert_called_once_with(
            rule_name="default",
            token="some.token",
            extra_blacklist_fields={},
            remove_token_from_track_model=True,
        )
