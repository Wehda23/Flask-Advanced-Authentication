from __future__ import annotations
"""Tests for import_handler utility."""

import pytest
from flask_advanced_auth.import_handler import import_handler


class TestValidatePath:
    def test_empty_string_raises(self):
        with pytest.raises(ImportError, match="non-empty string"):
            import_handler.grab("")

    def test_non_string_raises(self):
        with pytest.raises((ImportError, TypeError, ValueError)):
            import_handler.validate_path(123)


class TestParsePath:
    def test_single_segment_raises(self):
        with pytest.raises(ValueError, match="module.submodule.attribute"):
            import_handler.parse_path("singlemodule")

    def test_valid_path_splits_correctly(self):
        result = import_handler.parse_path("flask.Flask")
        assert result == ["flask", "Flask"]

    def test_deep_path_splits_correctly(self):
        result = import_handler.parse_path("os.path.join")
        assert result == ["os", "path", "join"]


class TestGrab:
    def test_grabs_real_class(self):
        Flask = import_handler.grab("flask.Flask")
        from flask import Flask as RealFlask
        assert Flask is RealFlask

    def test_grabs_real_function(self):
        join = import_handler.grab("os.path.join")
        from os.path import join as real_join
        assert join is real_join

    def test_invalid_module_raises_import_error(self):
        with pytest.raises(ImportError):
            import_handler.grab("totally.fake.Module")

    def test_invalid_attribute_raises_import_error(self):
        with pytest.raises(ImportError):
            import_handler.grab("flask.NonExistentClass")
