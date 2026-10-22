from __future__ import annotations
"""
Module contains the Database singleton — wraps a Flask-SQLAlchemy db instance.
"""

from typing import Optional, Any, Type
from flask_sqlalchemy import SQLAlchemy
from .import_handler import import_handler

_UNSET = object()


class DatabasePathNotProvided(Exception):
    """Raised when a database path is not provided on first initialization."""
    pass


class Database:
    """Singleton that holds and provides access to the Flask-SQLAlchemy db instance.

    The database instance is discovered via its dotted import path, e.g.
    ``"myapp.database.db"``.

    Example:
        >>> # First call — initialize with the path
        >>> Database("myapp.database.db")
        >>> # Subsequent calls — access the db
        >>> db = Database().db
        >>> db.session.query(MyModel).filter_by(id=1).first()
    """

    _instance: Type["Database"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self, path: Optional[str] = _UNSET) -> None:
        if path is None:
            raise DatabasePathNotProvided(
                "Database path must be provided on first initialization."
            )
        if path is not _UNSET:
            self.database_path = path
            self._initialized = True

    @classmethod
    def _reset(cls) -> None:
        """Reset singleton state. Intended for use in tests only."""
        cls._instance = None

    @property
    def database_path(self) -> str:
        """The dotted import path to the SQLAlchemy db instance."""
        if not hasattr(self, "_database_path"):
            raise DatabasePathNotProvided(
                "Database path has not been configured. Call initialize_jwt_authentication() first."
            )
        return self._database_path

    @database_path.setter
    def database_path(self, value: str) -> None:
        if not isinstance(value, str):
            raise DatabasePathNotProvided(
                f"Database path must be a string, got {type(value)}"
            )
        self._database_path = value

    @property
    def db(self) -> SQLAlchemy:
        """The SQLAlchemy database instance."""
        return self.grab_database(self.database_path)

    @staticmethod
    def grab_database(path: str) -> SQLAlchemy:
        """Import and return the SQLAlchemy db from the given dotted path."""
        return import_handler.grab(path=path)

    def model_instance_exists(self, model_class: Any, **kwargs: Any) -> Any:
        """Query the database for a model instance matching the given filters.

        Args:
            model_class: The SQLAlchemy model class.
            **kwargs: Filter arguments passed to ``filter_by()``.

        Returns:
            The first matching instance, or None.
        """
        return self.db.session.query(model_class).filter_by(**kwargs).first()

    def get_model_by_path(self, model_path: str) -> Type:
        """Return a model class from its dotted import path."""
        return import_handler.grab(model_path)

    def create_instance(self, instance: Any) -> None:
        """Add and commit a new model instance to the database."""
        self.db.session.add(instance)
        self.db.session.commit()

    def delete(self, instance: Any) -> None:
        """Delete and commit removal of a model instance from the database."""
        self.db.session.delete(instance)
        self.db.session.commit()

    def update(self, *args: Any, **kwargs: Any) -> None:
        """Commit any pending changes to the database session."""
        self.db.session.commit()
