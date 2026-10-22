from __future__ import annotations
"""Tests for TokenFactory."""

import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch
from flask_advanced_auth.factory import TokenFactory


class TestGenerateToken:
    def test_generate_token_returns_string(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_payload_has_type_access(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")
        payload = factory.validate_token(token, "default")
        assert payload["type"] == "access"

    def test_generate_token_none_rule_uses_default(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name=None)
        assert isinstance(token, str)


class TestGenerateRefreshToken:
    def test_generate_refresh_token_returns_string(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_refresh_token(rule_name="default")
        assert isinstance(token, str)

    def test_refresh_token_payload_has_type_refresh(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_refresh_token(rule_name="default")
        payload = factory.validate_token(token, "default")
        assert payload["type"] == "refresh"


class TestValidateToken:
    def test_valid_token_returns_payload(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")
        payload = factory.validate_token(token, "default")
        assert payload is not None
        assert "type" in payload

    def test_invalid_token_returns_none(self, jwt_rules):
        factory = TokenFactory()
        payload = factory.validate_token("not.a.real.token", "default")
        assert payload is None

    def test_wrong_secret_returns_none(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")
        # Decode with wrong key via proxy directly
        payload = factory.decode_token(token, "wrong-secret", "HS256")
        assert payload is None


class TestExtraPayload:
    def test_extra_payload_included_in_token(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default", extra_payload={"user_id": 99})
        payload = factory.validate_token(token, "default")
        assert payload["user_id"] == 99

    def test_extra_payload_must_be_dict_raises(self, jwt_rules):
        factory = TokenFactory()
        with pytest.raises(ValueError, match="dictionary"):
            factory.check_extra_payload("not-a-dict")

    def test_include_rule_name_in_payload(self, jwt_rules):
        factory = TokenFactory()
        token = factory.generate_token(rule_name="default", include_rule_name=True)
        payload = factory.validate_token(token, "default")
        assert payload["rule_name"] == "default"


class TestTrackToken:
    def test_track_token_calls_manager_register(self, jwt_rules):
        from flask_advanced_auth.jwt_rules import JWTAuthenticationRules
        # Override rule to enable track_created
        jwt_rules._rules["default"]["track_created"] = True
        jwt_rules._rules["default"]["track_created_table_path"] = "some.Track.Model"
        jwt_rules._rules["default"]["track_created_allow_duplicates"] = True

        factory = TokenFactory()
        mock_track_model_class = MagicMock()
        mock_track_model_instance = MagicMock()
        mock_track_model_class.return_value = mock_track_model_instance

        with patch.object(factory.manager, "get_model", return_value=mock_track_model_class):
            with patch.object(factory.manager, "register") as mock_register:
                with patch.object(factory.manager, "get_instance", return_value=None):
                    factory.track_token(
                        rule_name="default",
                        token="sometoken",
                        instance_id=1,
                        token_type="access",
                        additional_track_token_fields={},
                    )
                    mock_register.assert_called_once_with(mock_track_model_instance)
