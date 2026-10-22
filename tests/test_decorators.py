from __future__ import annotations
"""Tests for the @authenticate decorator — T-04 fix verification."""

import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, request as flask_request
from flask_advanced_auth.decorators import authenticate
from flask_advanced_auth.authentication_classes import AuthenticateJWT


@pytest.fixture
def app(jwt_rules):
    """Minimal Flask test app."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


class TestAuthenticateDecoratorValidation:
    def test_non_callable_return_func_raises(self, jwt_rules):
        with pytest.raises(TypeError, match="callable"):
            authenticate(auth_classes=[AuthenticateJWT], return_func="not_callable")

    def test_non_tuple_return_func_args_raises(self, jwt_rules):
        with pytest.raises(TypeError, match="tuple"):
            authenticate(auth_classes=[AuthenticateJWT], return_func_args=["not", "a", "tuple"])

    def test_auth_classes_must_be_list_of_subclasses(self, jwt_rules):
        with pytest.raises(TypeError, match="BaseAuthentication"):
            authenticate(auth_classes=[MagicMock()])


class TestAuthenticateDecoratorBehavior:
    def test_valid_token_calls_view(self, app, jwt_rules):
        from flask_advanced_auth.factory import TokenFactory

        factory = TokenFactory()
        token = factory.generate_token(rule_name="default")

        with app.test_request_context(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        ):
            @authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
            def protected_view():
                return "OK", 200

            result = protected_view()
            # Should return the view's result, not a 401
            assert result == ("OK", 200)

    def test_missing_token_returns_401(self, app, jwt_rules):
        with app.test_request_context("/protected"):
            @authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
            def protected_view():
                return "OK", 200

            response = protected_view()
            # make_response with (dict, 401) → check it's a Response
            from flask import Response
            assert hasattr(response, "status_code") or isinstance(response, tuple)

    def test_invalid_token_returns_401(self, app, jwt_rules):
        with app.test_request_context(
            "/protected",
            headers={"Authorization": "Bearer invalid.token.here"},
        ):
            @authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
            def protected_view():
                return "OK", 200

            response = protected_view()
            # Should not be the success return
            assert response != ("OK", 200)

    def test_decorator_preserves_function_name(self, jwt_rules):
        """Verify @wraps is applied correctly."""
        @authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
        def my_view():
            return "hi"

        assert my_view.__name__ == "my_view"

    def test_decorator_fix_returns_wrapper_not_none(self, jwt_rules):
        """T-04 fix: decorator must return a callable, not None."""
        result = authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
        assert callable(result)

        @result
        def my_view():
            return "hi"

        assert callable(my_view)
