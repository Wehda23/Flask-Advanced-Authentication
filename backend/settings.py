"""
File contains settings for flask application
"""

import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from a .env file
load_dotenv()


# Secret key
APPICATION_SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")

# Database
DATABASE: str = (
    f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/"
    f"{os.getenv('MYSQL_DATABASE')}"
)


# JWT Settings
SQLALCHEMY_JWT_DATABASE_PATH = "backend.models.db"

JWT_AUTHENTICATION_RULES: dict[str, dict] = {
    "default": {
        "description": "Token used to authenticate users",
        "secret_key": os.getenv("JWT_SECRET_KEY", "your-default-secret-key"),
        "algorithm": "HS256",
        "access_token_lifetime": timedelta(minutes=30),
        "track_created": True,
        "track_created_table_path": "backend.models.track_model.TrackModel",
    },
}
