from __future__ import annotations
"""
Module contains the import_handler utility class.
"""

import importlib
from typing import Any, Optional, NoReturn


class import_handler:
    """Utility class for dynamic import of classes from dotted path strings.

    Example:
        >>> MyModel = import_handler.grab("myapp.models.MyModel")
    """

    @staticmethod
    def validate_path(path: str) -> Optional[NoReturn]:
        """Validate that a dotted import path is a non-empty string."""
        if not isinstance(path, str) or not path:
            raise ValueError("Object path must be a non-empty string.")

    @staticmethod
    def parse_path(path: str) -> list[str]:
        """Split a dotted import path into a list of components."""
        path_list = path.split(".")
        if len(path_list) < 2:
            raise ValueError(
                "Class path must be in the format 'module.submodule.attribute'."
            )
        return path_list

    @staticmethod
    def import_module(name: str) -> Any:
        """Import a module by name."""
        return importlib.import_module(name)

    @classmethod
    def grab(cls, path: str) -> Any:
        """Import and return a class or object from a dotted path string.

        Args:
            path: Dotted import path, e.g. 'myapp.models.MyModel'.

        Returns:
            The imported object.

        Raises:
            ImportError: If the module or attribute cannot be found.
        """
        try:
            cls.validate_path(path=path)
            path_list: list[str] = cls.parse_path(path=path)
            module_name = path_list.pop(0)
            module = cls.import_module(module_name)
            imported_object = module
            for attribute in path_list:
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
