from __future__ import annotations
"""
Module contains the initiation of Flask-SQLAlchemy Database Model
"""

from flask_sqlalchemy import SQLAlchemy

try:
    from sqlalchemy.orm import DeclarativeBase
    class Base(DeclarativeBase):
        pass
    db: SQLAlchemy = SQLAlchemy(model_class=Base)
except ImportError:
    db: SQLAlchemy = SQLAlchemy()
