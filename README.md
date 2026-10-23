# flask-advanced-auth

[![PyPI version](https://img.shields.io/pypi/v/flask-advanced-auth.svg)](https://pypi.org/project/flask-advanced-auth/)
[![Python versions](https://img.shields.io/pypi/pyversions/flask-advanced-auth.svg)](https://pypi.org/project/flask-advanced-auth/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Wehda23/Flask-Advanced-Authentication/actions/workflows/ci.yml/badge.svg)](https://github.com/Wehda23/Flask-Advanced-Authentication/actions)
[![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)](https://github.com/Wehda23/Flask-Advanced-Authentication)

**flask-advanced-auth** is a production-grade, highly configurable JWT authentication extension for Flask and Flask-SQLAlchemy. It provides multi-rule support (different token lifetimes, secrets, and models for users vs. admins), built-in database token tracking, automatic token revocation (blacklisting), and clean route decorators.

---

## ✨ Features

- 🔑 **Multi-Rule Authentication**: Define distinct rules for different user tiers (e.g. `users`, `managers`, `api_clients`) with independent secrets, algorithms, and lifetimes.
- 🛡️ **Easy Route Protection**: Clean `@authenticate(auth_classes=[AuthenticateJWT])` decorator with customizable 401 response and model injection into `request.instance`.
- 🔄 **Access & Refresh Tokens**: Native support for short-lived access tokens and long-lived refresh tokens with convenient `refresh_access_token()` helper.
- 🚫 **Token Revocation (Blacklisting)**: Built-in revocation mechanism with database persistence and `logout()` helper.
- 📊 **Token Tracking**: Track issued tokens in the database to detect anomalies, enforce single-session limits, or audit activity.
- 🔌 **Multiple Extraction Strategies**: Extract tokens from `Authorization: Bearer <token>` headers, HTTP cookies, or URL query parameters.
- ⚡ **Pydantic Validation**: Strict configuration schema validation powered by Pydantic V2 with flexible aliases.
- 🧪 **Thoroughly Tested**: 100% test pass rate with ≥ 88% test coverage.

---

## 📦 Installation

```bash
pip install flask-advanced-auth
```

Or install with development dependencies:

```bash
pip install flask-advanced-auth[dev]
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Configure Rules & Bootstrap

```python
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
)

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-app-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
db = SQLAlchemy(app)

# Define your JWT rules
JWT_RULES = {
    "default": {
        "description": "Standard user access token",
        "secret_key": "your-jwt-secret-key",
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=15),
        "refresh_token_lifetime": timedelta(days=7),
        "token_header": "Bearer ",
    }
}

# Initialize flask-advanced-auth
initialize_jwt_authentication(
    database_path="app.db",
    rules=JWT_RULES,
)
```

### 2. Issue Tokens on Login

```python
@app.route("/api/login", methods=["POST"])
def login():
    username = request.json.get("username")
    
    factory = TokenFactory()
    access_token = factory.generate_token(
        rule_name="default",
        extra_payload={"sub": username},
    )
    refresh_token = factory.generate_refresh_token(
        rule_name="default",
        extra_payload={"sub": username},
    )
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })
```

### 3. Protect Routes

```python
@app.route("/api/dashboard")
@authenticate(auth_classes=[AuthenticateJWT], rule_name="default")
def dashboard():
    return jsonify({"message": "Welcome to your protected dashboard!"})
```

### 4. Refresh Tokens & Logout

```python
@app.route("/api/refresh", methods=["POST"])
def refresh():
    token = request.json.get("refresh_token")
    new_access_token = refresh_access_token(token, rule_name="default")
    return jsonify({"access_token": new_access_token})

@app.route("/api/logout", methods=["POST"])
def user_logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    logout(token, rule_name="default")
    return jsonify({"message": "Token revoked successfully."})
```

---

## ⚙️ Configuration Reference

Rules are passed as a dictionary where each key represents a rule name (e.g. `"default"`, `"admin"`):

| Field | Type | Default | Description |
|---|---|---|---|
| `description` | `str` | *Required* | Description of what this token rule is used for. |
| `secret_key` | `str` | *Required* | Secret signing key for encoding and decoding tokens. |
| `algorithm` | `str` | *Required* | JWT signing algorithm (e.g. `'HS256'`, `'RS256'`). |
| `access_token_lifetime` | `timedelta` | *Required* | Expiry duration for access tokens. |
| `refresh_token_lifetime` | `timedelta` | `None` | Expiry duration for refresh tokens. |
| `token_header` | `str` | `'Bearer '` | Expected header prefix in `Authorization` header. |
| `table` | `bool` | `False` | Whether to link tokens to a database entity. |
| `table_path` | `str` | `None` | Dotted import path to model class (e.g. `'myapp.models.User'`). |
| `track_created` | `bool` | `False` | Persist issued tokens to the database. |
| `track_created_table_path` | `str` | `None` | Dotted import path to TrackModel class. |
| `track_created_allow_duplicates` | `bool` | `True` | Allow multiple active tokens for the same user. |
| `blacklisted` | `bool` | `False` | Enable token blacklist checks on verification. |
| `blacklisted_table_path` | `str` | `None` | Dotted import path to BlackListModel class. |

---

## 🎯 Multi-Token Architecture Guide

You can define multiple token rules tailored for completely different purposes across your application:

```python
import os
from datetime import timedelta

JWT_AUTHENTICATION_RULES = {
    # 1. Stateful Login Token (Tracked in DB + Blacklisted)
    "user_login": {
        "description": "Standard app login",
        "secret_key": os.getenv("JWT_SECRET_USER"),
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=15),
        "refresh_token_lifetime": timedelta(days=7),
        "track_created": True,
        "track_created_table_path": "myapp.models.TrackedToken",
        "blacklisted": True,
        "blacklisted_table_path": "myapp.models.BlacklistToken",
    },

    # 2. Completely Stateless Email Verification (NO Database needed)
    "email_verification": {
        "description": "Email confirm token for registration",
        "secret_key": os.getenv("JWT_SECRET_EMAIL"),
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(hours=24),
        "table": False,
        "track_created": False,   # Zero DB overhead!
        "blacklisted": False,
    },

    # 3. Live Streaming / WebSocket Token (Extracted via URL Query Parameter)
    "live_stream": {
        "description": "Video stream viewer auth token",
        "secret_key": os.getenv("JWT_SECRET_STREAM"),
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(hours=3),
        "table": False,
        "track_created": False,
    },

    # 4. Password Reset Token (Strict, 10 minutes)
    "password_reset": {
        "description": "One-time password reset",
        "secret_key": os.getenv("JWT_SECRET_RESET"),
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=10),
        "table": False,
        "track_created": False,
    }
}
```

---

## 🧩 Authentication Strategies

You can choose how tokens are extracted by passing different authentication classes to `@authenticate`:

```python
from flask_advanced_auth import (
    authenticate,
    HeaderAuthentication,   # Reads Authorization: Bearer <token>
    CookieAuthentication,   # Reads token from HTTP cookies
    QueryParamAuthentication, # Reads ?token=<token>
)

# 1. From Authorization header
@app.route("/api/v1/data")
@authenticate(auth_classes=[HeaderAuthentication])
def api_data():
    return {"status": "ok"}

# 2. From Cookie
@app.route("/web/profile")
@authenticate(auth_classes=[CookieAuthentication])
def web_profile():
    return {"status": "ok"}

# 3. From URL parameter (e.g., SSE or WebSocket connection handshake)
@app.route("/stream")
@authenticate(auth_classes=[QueryParamAuthentication])
def stream():
    return {"status": "connected"}
```

---

## 🗄️ Database Model Mixins

When enabling `track_created` or `blacklisted`, use our ready-to-use SQLAlchemy model mixins:

```python
from flask_advanced_auth.models import AbstractTrackModelMixin, AbstractBlackListModelMixin
from myapp.database import db

class TrackedToken(db.Model, AbstractTrackModelMixin):
    __tablename__ = "tracked_tokens"

class BlacklistedToken(db.Model, AbstractBlackListModelMixin):
    __tablename__ = "blacklisted_tokens"
```

---

## 🧪 Running Tests

```bash
# Run tests with coverage
pytest -v

# Run single test module
pytest tests/test_decorators.py -v
```

---

## 🤝 Contributing

Contributions are welcome! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and guidelines.

---

## 💖 Support My Work

If you find my free content and projects helpful, consider supporting me to enable more learning resources for the community. Your contributions will go towards creating new content and maintaining existing projects.

### Ways to Support

You can support the project by buying me a coffee:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/waheedKh)

Your generosity is greatly appreciated!

### Why Support?

By supporting this project, you help ensure the continued availability of free educational content and the development of new projects. Your contribution makes a meaningful impact on the community of learners.

Thank you for your support!

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
