"""
Module contains users api views
"""

from flask import Response, make_response
from .route import users_api
from backend.models import db, Users
from backend.admin.auth import Database, import_handler
from backend.admin.auth.decorators import authenticate

@users_api.route("")
@authenticate()
def users() -> Response:
    """
    Users api view
    """
    users: Users = import_handler.grab("backend.models.Users")
    print(type(users))
    print(str(users))
    print(users is Users)
    print(Users.__tablename__)
    print(Database().db.session.query(users).filter_by(id=1).first())
    print(Database().model_instance_exists(users, id=1))
    return make_response({"test": 12, "Working": True, "API": "Users"}, 200)
