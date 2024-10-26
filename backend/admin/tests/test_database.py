"""
Unittesting Module for Database Class
"""

import unittest
from unittest.mock import patch, MagicMock
from backend.admin.auth.database import Database, DatabasePathNotProvided


class TestDatabase(unittest.TestCase):
    @patch("importlib.import_module")
    def test_singleton_pattern(self, mock_import_module):
        mock_import_module.return_value = MagicMock()

        db_instance1 = Database("backend.path.to.yourdatabase")
        db_instance2 = Database()

        self.assertIs(db_instance1, db_instance2, "Database instances are not the same")

    def test_database_path_not_provided(self):
        with self.assertRaises(DatabasePathNotProvided):
            Database(None)

    def test_database_path_setter(self):
        db_instance = Database("backend.path.to.yourdatabase")
        self.assertEqual(db_instance.database_path, "backend.path.to.yourdatabase")

        with self.assertRaises(DatabasePathNotProvided):
            db_instance.database_path = 123  # Non-string path

    @patch("importlib.import_module")
    def test_grab_database(self, mock_import_module):
        mock_import_module.return_value = MagicMock()
        mock_import_module.return_value.some_attribute = "some_value"

        db_instance = Database("backend.path.to.yourdatabase")
        self.assertIsNotNone(db_instance.db)

    @patch("importlib.import_module")
    def test_import_module_failure(self, mock_import_module):
        mock_import_module.side_effect = ModuleNotFoundError("Module not found")

        db_instance = Database("backend.path.to.yourdatabase")
        with self.assertRaises(ImportError):
            _ = db_instance.db


if __name__ == "__main__":
    unittest.main()
