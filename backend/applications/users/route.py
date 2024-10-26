"""
Module creating the blueprint for users api

Route prefix `/api/users`

```py
from .route import users_api
```
"""

from flask import Blueprint


# Declare route prefix
url_prefix: str = "/api/users"

# Blueprint
users_api: Blueprint = Blueprint("users_api", __name__, url_prefix=url_prefix)

from . import views
