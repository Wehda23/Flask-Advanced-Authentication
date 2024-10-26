"""
Module to create and run flask application
"""

from backend import create_app, database_init, register_routes
from backend.settings import JWT_AUTHENTICATION_RULES, SQLALCHEMY_JWT_DATABASE_PATH
from backend.admin.auth import (
    JWTAuthenticationRules,
    initialize_jwt_authentication,
    Database,
)
from flask import Flask


# Create flask application
app: Flask = create_app(mode="development")
app.url_map.strict_slashes = False


# Initialize database
database_init(app)

# Register Flask BluePrints
register_routes(app)

print(JWT_AUTHENTICATION_RULES)
# Integrate JWT Package
initialize_jwt_authentication(SQLALCHEMY_JWT_DATABASE_PATH, JWT_AUTHENTICATION_RULES)

print(JWTAuthenticationRules().rules)
# Run Application
if __name__ == "__main__":
    app.run()
