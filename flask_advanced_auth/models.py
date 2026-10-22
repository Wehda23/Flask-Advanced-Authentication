from __future__ import annotations
"""
Module contains abstract model mixins for TrackModel and BlackListModel.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from typing import Any


class AbstractTrackModelMixin:
    """SQLAlchemy model mixin for tracking issued JWT tokens.

    Example:
        >>> from flask_advanced_auth.models import AbstractTrackModelMixin
        >>> from myapp.database import db
        >>>
        >>> class TrackedToken(db.Model, AbstractTrackModelMixin):
        ...     __tablename__ = "tracked_tokens"
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(2056), nullable=False, unique=True, index=True)
    instance_id = Column(String(256), nullable=False, index=True)
    token_type = Column(String(32), nullable=False, default="access")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class AbstractBlackListModelMixin:
    """SQLAlchemy model mixin for persisting revoked/blacklisted JWT tokens.

    Example:
        >>> from flask_advanced_auth.models import AbstractBlackListModelMixin
        >>> from myapp.database import db
        >>>
        >>> class BlacklistedToken(db.Model, AbstractBlackListModelMixin):
        ...     __tablename__ = "blacklisted_tokens"
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(2056), nullable=False, unique=True, index=True)
    reason = Column(String(256), nullable=True, default="logout")
    blacklisted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
