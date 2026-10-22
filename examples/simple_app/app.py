"""
Minimal example application using flask-advanced-auth.
Run with: python app.py
"""

from datetime import timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_advanced_auth import (
    initialize_jwt_authentication,
    authenticate,
    AuthenticateJWT,
    TokenFactory,
    refresh_access_token,
    logout,
    AbstractTrackModelMixin,
    AbstractBlackListModelMixin,
)

# 1. Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key-change-in-production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 2. Setup Database
db = SQLAlchemy(app)


class TrackedToken(db.Model, AbstractTrackModelMixin):
    __tablename__ = "tracked_tokens"


class BlacklistedToken(db.Model, AbstractBlackListModelMixin):
    __tablename__ = "blacklisted_tokens"


# 3. Configure Authentication Rules
JWT_RULES = {
    "default": {
        "description": "Standard user access token",
        "secret_key": "jwt-signing-secret",
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=15),
        "refresh_token_lifetime": timedelta(days=7),
        "token_header": "Bearer ",
        "track_created": True,
        "track_created_table_path": "app.TrackedToken",
        "blacklisted": True,
        "blacklisted_table_path": "app.BlacklistedToken",
    }
}

# 4. Bootstrap flask-advanced-auth
initialize_jwt_authentication(
    database_path="app.db",
    rules=JWT_RULES,
)


# 5. Define Routes
@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate user and issue JWT access + refresh tokens."""
    data = request.get_json() or {}
    username = data.get("username", "guest")

    factory = TokenFactory()
    access_token = factory.generate_token(
        rule_name="default",
        extra_payload={"username": username},
    )
    refresh_token = factory.generate_refresh_token(
        rule_name="default",
        extra_payload={"username": username},
    )

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in_minutes": 15,
    }), 200


@app.route("/api/protected", methods=["GET"])
@authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
def protected():
    """Protected endpoint — requires valid Bearer token."""
    return jsonify({
        "message": "Access granted to secure resource!",
        "status": "authenticated",
    }), 200


@app.route("/api/refresh", methods=["POST"])
def refresh():
    """Exchange a valid refresh token for a fresh access token."""
    data = request.get_json() or {}
    token = data.get("refresh_token")
    if not token:
        return jsonify({"error": "refresh_token is required"}), 400

    new_access_token = refresh_access_token(token, rule_name="default")
    return jsonify({"access_token": new_access_token}), 200


@app.route("/api/logout", methods=["POST"])
def user_logout():
    """Revoke an active token."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
        logout(token, rule_name="default")
        return jsonify({"message": "Successfully logged out"}), 200
    return jsonify({"error": "Authorization header missing"}), 400


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print("Example app running at http://127.0.0.1:5000")
    app.run(debug=True)
