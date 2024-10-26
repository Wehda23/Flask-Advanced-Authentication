"""
Module contains model handlers
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from .database import Database


class AbstractManager(ABC):
    """Abstract class for model managers"""

    database = None

    @abstractmethod
    def get_model(self, model_path: str) -> Any:
        """
        Get a model by name

        Args:
            model_path (str): Path to the model eg. "backend.models.ModelName"
        Returns:
            Any: Model object
        """
        pass

    @abstractmethod
    def register(self, instance: object) -> None:
        """
        Register a model instance
        """
        pass

    @abstractmethod
    def unregister(self, instance: object) -> None:
        """
        Unregister a model instance
        """
        pass

    @abstractmethod
    def get_instance(self, *args: Any, **kwargs: Any) -> Any:
        """
        Get a model instance by kwargs
        """
        pass


class ModelManager(AbstractManager):
    """Model manager for model"""

    database: Database = Database()

    def get_model(self, model_path: str) -> Any:
        """
        Get a model by path

        Args:
            model_path (str): Path to the model eg. "backend.models.ModelName"

        Returns:
            Any: Model object
        """
        return self.database.get_model_by_path(model_path)

    def register(self, instance: object) -> None:
        """Register a model instance"""
        self.database.create_instance(instance)

    def unregister(self, instance: object) -> None:
        """
        Unregister a model instance
        """
        self.database.delete(instance)

    def get_instance(
        self,
        model_class: Optional[object] = None,
        model_path: str = None,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """
        Get a model instance by kwargs
        """
        # Check both parameters are not None
        if model_class is None and model_path is None:
            raise ValueError("Either model_class or model_path must be provided")
        # If model_class is not provided but model path is then grab the model_Class from path
        if model_class is None:
            model_class = self.get_model(model_path)
        # Return the model instance
        return self.database.model_instance_exists(model_class=model_class, **kwargs)
