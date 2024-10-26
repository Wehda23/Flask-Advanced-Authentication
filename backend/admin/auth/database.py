"""
Module contains Class Database which handles retrieving SQLAlchemy Database from path
"""

from typing import Optional, Any, Type
from flask_sqlalchemy import SQLAlchemy
from .import_handler import import_handler


# Database Exceptions
class DatabasePathNotProvided(Exception):
    pass


class Database:
    """
    Class That retrieves SQLAlchemy Database implements Singleton design pattern.

    This class uses the following to grab the SQLAlchemy database
    ```py
    import importlib

    database_path: str = "backend.path.path2.path3.yourdatabase"
    db = importlib.import_module(path)
    ```

    Calling the class will return the SQLAlchemy Database and will not
        return class Database instance

    ```py
    def __new__(cls, *args: Any, **kwargs: Any) -> "Database":
    if cls._instance is None:
        cls._instance = super(Database, cls).__new__(cls)
    # Will return SQLAlchemy Database not class instance.
    return cls._instance.db
    ```

    Note that it returns the `SQLAlchemy` Database

    ### Example usage after initiation:

    ```py
    from .database import Database
    from flask_sqlalchemy import SQLAlchemy

    # First initiation of class
    database: Database = Database("backend.path.path2.path3.yourdatabase")

    assert type(database) == Database # True

    # Second call will the SQLAlchemy Database
    db = Database().db

    assert isinstance(db, SQLAlchemy) # True

    # Use SQLAlchemy Database
    db.session.query("Model_Name").filter_by(id=1)
    ```
    """

    _instance: Type["Database"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        # Will return SQLAlchemy Database not class instance.
        return cls._instance

    def __init__(self, path: Optional[str] = None) -> None:
        """
        Class Constructor
        """
        if not hasattr(self, "_initialized"):  # Initialize only once
            if path is None:
                raise DatabasePathNotProvided("Database path must be provided")
            self.database_path = path
            self._initialized = True

    @property
    def database_path(self) -> str:
        """
        Retrieves database path
        """
        return self._database_path

    @database_path.setter
    def database_path(self, value: str) -> None:
        """
        Setter Property for database path
        """
        if not isinstance(value, str):
            raise DatabasePathNotProvided(
                f"Database Path must be a string, you entered type: {type(value)}"
            )
        self._database_path = value

    @property
    def db(self) -> SQLAlchemy:
        """
        Retrieves SQLAlchemy Database from path.

        Returns:
            The imported SQLAlchemy database module.

        Raises:
            ImportError: If the module or attribute cannot be found.
        """
        return self.grab_database(self.database_path)

    @staticmethod
    def grab_database(path: str) -> SQLAlchemy:
        """
        Grabs the database from the path.
        Returns:
            The imported SQLAlchemy database module.

        Raises:
            ImportError: If the module or attribute cannot be found.
        """
        return import_handler.grab(path=path)

    def model_instance_exists(self, model_class: str, **kwargs) -> object:
        """
        Method used to check if instance exists in the model.

        Args:
            model_class (Object): Model Class
            instance_id (Any): ID of the instance.
            kwargs (dict): Keyword arguments to be used inside filter_by method.

        Returns:
            bool: True if instance exists, False otherwise.
        """
        return self.db.session.query(model_class).filter_by(**kwargs).first()

    def get_model_by_path(self, model_path: str) -> Type:
        """
        Retrieve the model class by its path.

        Args:
            model_path (str): The path of the model.

        Returns:
            The model class corresponding to the given path.
        """
        return import_handler.grab(model_path)

    def create_instance(self, instance) -> None:
        """
        Creates a new instance of the model.
        Args:
        instance: The instance to be created.
        Returns:
        The created instance.
        """
        self.db.session.add(instance)
        self.db.session.commit()

    def delete(self, instance: Any) -> None:
        """
        Deletes the instance from the database.
        Args:
        instance: The instance to be deleted.
        """
        self.db.session.delete(instance)
        self.db.session.commit()

    def update(self, *args: Any, **kwargs: Any) -> None:
        """
        Updates the instance in the database.
        """
        self.db.session.commit()
