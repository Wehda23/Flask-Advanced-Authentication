from __future__ import annotations
"""Tests for model mixins."""

from flask_advanced_auth.models import AbstractTrackModelMixin, AbstractBlackListModelMixin
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer

Base = declarative_base()


class TrackedToken(Base, AbstractTrackModelMixin):
    __tablename__ = "test_tracked_tokens"


class BlacklistedToken(Base, AbstractBlackListModelMixin):
    __tablename__ = "test_blacklisted_tokens"


class TestModelMixins:
    def test_tracked_model_columns_exist(self):
        assert hasattr(TrackedToken, "id")
        assert hasattr(TrackedToken, "token")
        assert hasattr(TrackedToken, "instance_id")
        assert hasattr(TrackedToken, "token_type")
        assert hasattr(TrackedToken, "created_at")

    def test_blacklisted_model_columns_exist(self):
        assert hasattr(BlacklistedToken, "id")
        assert hasattr(BlacklistedToken, "token")
        assert hasattr(BlacklistedToken, "reason")
        assert hasattr(BlacklistedToken, "blacklisted_at")
