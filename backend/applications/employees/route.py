"""
Module creating the blueprint for employees api

Route prefix `/api/employees`

```py
from .route import employees_api
```
"""

from flask import Blueprint


# Declare route prefix
url_prefix: str = "/api/employees"

# Blueprint
employees_api: Blueprint = Blueprint("employees_api", __name__, url_prefix=url_prefix)

from . import views
