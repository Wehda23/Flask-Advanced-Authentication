"""
Module Contains Flask Configurations
"""

import os
from abc import ABC
from backend.settings import DATABASE, APPICATION_SECRET_KEY

# Load environment variables from a .env file


class Config(ABC):
    """
    Base configuration class. Contains default settings.
    """

    DEBUG = False
    TESTING = False
    SECRET_KEY = APPICATION_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """
    Development configuration class. Extends the base configuration class.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"


class TestingConfig(Config):
    """
    Testing configuration class. Extends the base configuration class.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"


class ProductionConfig(Config):
    """
    Production configuration class. Extends the base configuration class.
    """

    SQLALCHEMY_DATABASE_URI = DATABASE
    SECRET_KEY = os.getenv("SECRET_KEY", "your-production-secret-key")


# Dictionary mapping mode names to config classes
config_modes: dict[str, Config] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

"""
{
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
"""
