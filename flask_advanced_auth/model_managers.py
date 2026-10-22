from __future__ import annotations
"""
Module contains model manager classes — bridge between business logic and the database.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from .database import Database


class AbstractManager(ABC):
    """Abstract interface for model managers."""

    database = None

    @abstractmethod
    def get_model(self, model_path: str) -> Any:
        """Get a model class by its dotted import path."""
        pass

    @abstractmethod
    def register(self, instance: object) -> None:
        """Persist a new model instance to the database."""
        pass

    @abstractmethod
    def unregister(self, instance: object) -> None:
        """Delete a model instance from the database."""
        pass

    @abstractmethod
    def get_instance(self, *args: Any, **kwargs: Any) -> Any:
        """Retrieve a model instance matching the given kwargs."""
        pass


class ModelManager(AbstractManager):
    """Concrete model manager backed by the Database singleton."""

    database: Database = Database()

    def get_model(self, model_path: str) -> Any:
        """Get a model class by its dotted import path.

        Args:
            model_path: Dotted path, e.g. 'myapp.models.User'.

        Returns:
            The model class.
        """
        return self.database.get_model_by_path(model_path)

    def register(self, instance: object) -> None:
        """Add and commit a model instance."""
        self.database.create_instance(instance)

    def unregister(self, instance: object) -> None:
        """Delete and commit removal of a model instance."""
        self.database.delete(instance)

    def get_instance(
        self,
        model_class: Optional[object] = None,
        model_path: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Retrieve a model instance by filter kwargs.

        Args:
            model_class: The model class (optional if model_path is given).
            model_path: Dotted import path to the model class (optional if model_class given).
            **kwargs: Filter arguments for the database query.

        Returns:
            The first matching instance, or None.

        Raises:
            ValueError: If neither model_class nor model_path is provided.
        """
        if model_class is None and model_path is None:
            raise ValueError("Either model_class or model_path must be provided")
        if model_class is None:
            model_class = self.get_model(model_path)
        return self.database.model_instance_exists(model_class=model_class, **kwargs)
