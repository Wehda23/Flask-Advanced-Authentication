"""
Module creating the blueprint for managers api

Route prefix `/api/managers`

```py
from .route import managers_api
```
"""

from flask import Blueprint


# Declare route prefix
url_prefix: str = "/api/managers"

# Blueprint
managers_api: Blueprint = Blueprint("managers_api", __name__, url_prefix=url_prefix)

from .views.managers_views import *
