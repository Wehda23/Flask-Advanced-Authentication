from __future__ import annotations
"""Tests for Database singleton."""

import pytest
from unittest.mock import patch, MagicMock
from flask_advanced_auth.database import Database, DatabasePathNotProvided


class TestDatabaseSingleton:
    def test_singleton_same_instance(self):
        db1 = Database("some.database.path")
        db2 = Database()
        assert db1 is db2

    def test_no_path_on_first_init_raises(self):
        with pytest.raises(DatabasePathNotProvided):
            Database(None)

    def test_non_string_path_raises(self):
        with pytest.raises(DatabasePathNotProvided):
            d = Database("valid.path")
            d.database_path = 12345

    def test_database_path_stored_correctly(self):
        db = Database("myapp.database.db")
        assert db.database_path == "myapp.database.db"

    def test_reset_allows_reinit(self):
        Database("path.one")
        Database._reset()
        db = Database("path.two")
        assert db.database_path == "path.two"


class TestGrabDatabase:
    @patch("flask_advanced_auth.import_handler.import_handler.grab")
    def test_grab_database_calls_import_handler(self, mock_grab):
        mock_grab.return_value = MagicMock()
        result = Database.grab_database("some.db.path")
        mock_grab.assert_called_once_with(path="some.db.path")
        assert result is not None

    @patch("flask_advanced_auth.import_handler.import_handler.grab")
    def test_grab_database_raises_on_bad_path(self, mock_grab):
        mock_grab.side_effect = ImportError("Module not found")
        with pytest.raises(ImportError):
            Database.grab_database("bad.path.here")


class TestDatabaseOperations:
    @patch("flask_advanced_auth.import_handler.import_handler.grab")
    def test_model_instance_exists_calls_session_query(self, mock_grab):
        mock_db = MagicMock()
        mock_grab.return_value = mock_db
        db = Database("mock.db")

        MockModel = MagicMock()
        db.model_instance_exists(MockModel, id=1)
        mock_db.session.query.assert_called_once_with(MockModel)

    @patch("flask_advanced_auth.import_handler.import_handler.grab")
    def test_create_instance_commits(self, mock_grab):
        mock_db = MagicMock()
        mock_grab.return_value = mock_db
        db = Database("mock.db")

        instance = MagicMock()
        db.create_instance(instance)
        mock_db.session.add.assert_called_once_with(instance)
        mock_db.session.commit.assert_called()

    @patch("flask_advanced_auth.import_handler.import_handler.grab")
    def test_delete_commits(self, mock_grab):
        mock_db = MagicMock()
        mock_grab.return_value = mock_db
        db = Database("mock.db")

        instance = MagicMock()
        db.delete(instance)
        mock_db.session.delete.assert_called_once_with(instance)
        mock_db.session.commit.assert_called()
