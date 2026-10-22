from __future__ import annotations
"""Tests for BlackListed token revocation."""

import pytest
from unittest.mock import MagicMock, patch
from flask_advanced_auth.blacklist_token import BlackListed


@pytest.fixture
def blacklist_rules(jwt_rules):
    """JWT rules with blacklisting enabled."""
    jwt_rules._rules["default"]["blacklisted"] = True
    jwt_rules._rules["default"]["blacklisted_table_path"] = "some.BlackList.Model"
    jwt_rules._rules["default"]["track_created"] = True
    jwt_rules._rules["default"]["track_created_table_path"] = "some.Track.Model"
    return jwt_rules


class TestIsBlacklisted:
    def test_returns_false_when_blacklist_disabled(self, jwt_rules):
        """T-05 fix: rule_name is properly passed to get_blacklisted."""
        bl = BlackListed()
        # default rule has blacklisted=False in conftest
        result = bl.is_blacklisted("default", "some.token")
        assert result is False

    def test_returns_instance_when_token_blacklisted(self, blacklist_rules):
        bl = BlackListed()
        mock_model = MagicMock()
        mock_instance = MagicMock()

        with patch.object(bl._manager, "get_model", return_value=mock_model):
            with patch.object(bl._manager, "get_instance", return_value=mock_instance):
                result = bl.is_blacklisted("default", "blacklisted.token")
                assert result is mock_instance

    def test_returns_none_when_token_not_blacklisted(self, blacklist_rules):
        bl = BlackListed()
        mock_model = MagicMock()

        with patch.object(bl._manager, "get_model", return_value=mock_model):
            with patch.object(bl._manager, "get_instance", return_value=None):
                result = bl.is_blacklisted("default", "clean.token")
                assert result is None


class TestBlacklist:
    def test_blacklist_creates_db_record(self, blacklist_rules):
        bl = BlackListed()
        mock_model_class = MagicMock()
        mock_instance = MagicMock()
        mock_model_class.return_value = mock_instance

        with patch.object(bl._manager, "get_model", return_value=mock_model_class):
            with patch.object(bl._manager, "register") as mock_register:
                bl.blacklist("default", "some.token")
                mock_register.assert_called_once_with(mock_instance)

    def test_blacklist_removes_from_track_model_when_requested(self, blacklist_rules):
        bl = BlackListed()
        mock_model_class = MagicMock()
        mock_track_instance = MagicMock()
        mock_model_class.return_value = MagicMock()

        with patch.object(bl._manager, "get_model", return_value=mock_model_class):
            with patch.object(bl._manager, "register"):
                with patch.object(bl._manager, "get_instance", return_value=mock_track_instance):
                    with patch.object(bl._manager, "unregister") as mock_unregister:
                        bl.blacklist("default", "some.token", remove_token_from_track_model=True)
                        mock_unregister.assert_called_once_with(mock_track_instance)


class TestUnregisterFromTrackModel:
    def test_unregister_calls_manager_unregister(self, blacklist_rules):
        bl = BlackListed()
        mock_instance = MagicMock()
        mock_model = MagicMock()

        with patch.object(bl._manager, "get_model", return_value=mock_model):
            with patch.object(bl._manager, "get_instance", return_value=mock_instance):
                with patch.object(bl._manager, "unregister") as mock_unreg:
                    bl.unregister_token_from_track_model("default", "some.token")
                    mock_unreg.assert_called_once_with(mock_instance)

    def test_unregister_skips_if_not_found(self, blacklist_rules):
        bl = BlackListed()
        mock_model = MagicMock()

        with patch.object(bl._manager, "get_model", return_value=mock_model):
            with patch.object(bl._manager, "get_instance", return_value=None):
                with patch.object(bl._manager, "unregister") as mock_unreg:
                    bl.unregister_token_from_track_model("default", "ghost.token")
                    mock_unreg.assert_not_called()
