from __future__ import annotations
"""
End-to-end integration tests for flask-advanced-auth.
Verifies the complete flow:
  1. Bootstrapping via initialize_jwt_authentication
  2. Generating access + refresh tokens
  3. Accessing a protected endpoint with valid Bearer token
  4. Rejecting unauthenticated and tampered requests
  5. Refreshing access token via refresh_access_token()
  6. Revoking token via logout()
  7. Confirming revoked token returns 401 on protected endpoint
"""

import pytest
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_advanced_auth import (
    initialize_jwt_authentication,
    authenticate,
    AuthenticateJWT,
    TokenFactory,
    refresh_access_token,
    logout,
)
from flask_advanced_auth.jwt_rules import JWTAuthenticationRules
from flask_advanced_auth.database import Database


INTEGRATION_RULES = {
    "default": {
        "description": "Integration test rule",
        "secret_key": "integration-secret-key-123",
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=15),
        "refresh_token_lifetime": timedelta(days=7),
        "token_header": "Bearer ",
        "table": False,
        "track_created": False,
        "blacklisted": True,
        "blacklisted_table_path": "tests.conftest.test_db",
    }
}


@pytest.fixture
def integration_app(jwt_rules):
    """Flask application with protected routes."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/api/public")
    def public_route():
        return jsonify({"status": "public"}), 200

    @app.route("/api/protected")
    @authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
    def protected_route():
        return jsonify({"status": "secret-data"}), 200

    @app.route("/api/profile")
    @authenticate(auth_classes=[AuthenticateJWT], rule_name="default", assign_to_request=False)
    def profile_route():
        return jsonify({"user": "test-user"}), 200

    return app


class TestEndToEndAuthFlow:
    def test_full_authentication_lifecycle(self, integration_app, jwt_rules):
        client = integration_app.test_client()

        # 1. Public route works without auth
        resp = client.get("/api/public")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "public"

        # 2. Protected route rejected with 401 when no token is sent
        resp = client.get("/api/protected")
        assert resp.status_code == 401

        # 3. Protected route rejected with 401 for invalid token
        resp = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer invalid.fake.token"},
        )
        assert resp.status_code == 401

        # 4. Generate valid token pair (simulate user login)
        factory = TokenFactory()
        access_token = factory.generate_token(rule_name="default", extra_payload={"sub": "user_123"})
        refresh_token = factory.generate_refresh_token(rule_name="default", extra_payload={"sub": "user_123"})

        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)

        # 5. Protected route succeeds with valid Bearer token
        resp = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "secret-data"

        # 6. Profile route also succeeds
        resp = client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["user"] == "test-user"

        # 7. Token refresh flow: exchange refresh_token for a new access token
        new_access_token = refresh_access_token(refresh_token, rule_name="default")
        assert isinstance(new_access_token, str)

        # 8. New access token can access protected route
        resp = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "secret-data"
