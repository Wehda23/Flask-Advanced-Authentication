"""
Model Contains Class Import handler
"""

import importlib
from typing import Any, Optional, NoReturn


class import_handler:
    @staticmethod
    def validate_path(path: str) -> Optional[NoReturn]:
        """
        Method to validate the path
        """
        # Ensure the path is valid
        if not isinstance(path, str) or not path:
            raise ValueError("object path must be a non-empty string.")

    @staticmethod
    def parse_path(path: str) -> list[str]:
        """
        Method used to parse object import path
        """
        # Split the path into module and attributes
        path_list = path.split(".")
        if len(path_list) < 2:
            raise ValueError(
                "class path must be in the format 'module.submodule.attribute'."
            )
        return path_list

    @staticmethod
    def import_module(name: str) -> Any:
        """
        Method used to import the module
        """
        # Import the module
        module = importlib.import_module(name)
        return module

    @classmethod
    def grab(cls, path: str) -> Any:
        """
        Grabs the class from the path

        Args:
            path (str): to the class

        Raises:
            ImportError: If the module or attribute cannot be found.

        Returns:
            class (object): imported class object.
        """
        try:
            # Validate path
            cls.validate_path(path=path)
            path_list: list[str] = cls.parse_path(path=path)
            # Import the module
            module_name = path_list.pop(0)
            module = cls.import_module(module_name)
            # Traverse attributes
            attributes = path_list
            imported_object = module
            for attribute in attributes:
                imported_object = getattr(imported_object, attribute)
            return imported_object
        except ModuleNotFoundError as e:
            raise ImportError(f"Module '{path}' could not be found: {e}")
        except AttributeError as e:
            raise ImportError(f"Attribute '{path}' could not be found in module: {e}")
        except ValueError as e:
            raise ImportError(f"Invalid object path '{path}': {e}")
        except Exception as e:
            raise ImportError(
                f"An unexpected error occurred while importing '{path}': {e}"
            )
