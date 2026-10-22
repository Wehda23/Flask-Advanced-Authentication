from __future__ import annotations
"""
Shared pytest fixtures for flask-advanced-auth test suite.
"""

import copy
import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# ── In-memory SQLite app + db ────────────────────────────────────────────────

try:
    from sqlalchemy.orm import DeclarativeBase
    class Base(DeclarativeBase):
        pass
    test_db = SQLAlchemy(model_class=Base)
except ImportError:
    test_db = SQLAlchemy()


def create_test_app() -> Flask:
    """Create a minimal Flask app with an in-memory SQLite database."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "test-secret"
    test_db.init_app(app)
    return app


@pytest.fixture(scope="session")
def test_app():
    """Session-scoped Flask test application."""
    app = create_test_app()
    return app


@pytest.fixture(scope="session")
def db_models(test_app):
    """Create all test tables in the in-memory SQLite DB."""
    with test_app.app_context():
        test_db.create_all()
        yield test_db
        test_db.drop_all()


# ── Standard JWT rules fixture ───────────────────────────────────────────────

DEFAULT_RULES = {
    "default": {
        "description": "Test default rule",
        "secret_key": "test-secret-key",
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=30),
        "refresh_token_lifetime": timedelta(days=7),
        "token_header": "Bearer ",
        "table": False,
        "track_created": False,
        "blacklisted": False,
    }
}


# ── Reset singletons between tests ──────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singletons before and after each test to ensure isolation."""
    from flask_advanced_auth.jwt_rules import JWTAuthenticationRules
    from flask_advanced_auth.database import Database
    JWTAuthenticationRules._reset()
    Database._reset()
    yield
    JWTAuthenticationRules._reset()
    Database._reset()


@pytest.fixture
def jwt_rules(reset_singletons):
    """Initialized JWTAuthenticationRules singleton with default test rules."""
    from flask_advanced_auth.jwt_rules import JWTAuthenticationRules
    return JWTAuthenticationRules(rules=copy.deepcopy(DEFAULT_RULES), default_rule="default")


@pytest.fixture
def mock_db():
    """A mock Database singleton for tests that don't need a real DB."""
    with patch("flask_advanced_auth.database.Database") as mock:
        db_instance = MagicMock()
        mock.return_value = db_instance
        yield db_instance
