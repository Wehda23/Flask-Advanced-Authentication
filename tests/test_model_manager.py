from __future__ import annotations
"""Tests for ModelManager."""

import pytest
from unittest.mock import MagicMock, patch
from flask_advanced_auth.model_managers import ModelManager


@pytest.fixture
def manager():
    return ModelManager()


class TestGetModel:
    def test_get_model_calls_database_get_model_by_path(self, manager):
        mock_class = MagicMock()
        with patch.object(manager.database, "get_model_by_path", return_value=mock_class) as mock_get:
            result = manager.get_model("some.Model.Path")
            mock_get.assert_called_once_with("some.Model.Path")
            assert result is mock_class


class TestRegister:
    def test_register_calls_create_instance(self, manager):
        instance = MagicMock()
        with patch.object(manager.database, "create_instance") as mock_create:
            manager.register(instance)
            mock_create.assert_called_once_with(instance)


class TestUnregister:
    def test_unregister_calls_delete(self, manager):
        instance = MagicMock()
        with patch.object(manager.database, "delete") as mock_delete:
            manager.unregister(instance)
            mock_delete.assert_called_once_with(instance)


class TestGetInstance:
    def test_get_instance_with_model_class(self, manager):
        MockModel = MagicMock()
        with patch.object(manager.database, "model_instance_exists", return_value="found") as mock_exists:
            result = manager.get_instance(model_class=MockModel, id=1)
            mock_exists.assert_called_once_with(model_class=MockModel, id=1)
            assert result == "found"

    def test_get_instance_with_model_path(self, manager):
        MockModel = MagicMock()
        with patch.object(manager.database, "get_model_by_path", return_value=MockModel):
            with patch.object(manager.database, "model_instance_exists", return_value="found"):
                result = manager.get_instance(model_path="some.Model.Path", id=1)
                assert result == "found"

    def test_get_instance_requires_at_least_one_arg(self, manager):
        with pytest.raises(ValueError, match="model_class or model_path"):
            manager.get_instance()
