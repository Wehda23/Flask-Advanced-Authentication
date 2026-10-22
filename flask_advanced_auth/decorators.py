from __future__ import annotations
"""
Module contains the @authenticate decorator for protecting Flask routes.
"""

from functools import wraps
from flask import request, make_response, Response
from typing import Any, Callable, Tuple, Union, Type, Optional
from .authentication_classes import BaseAuthentication
from .jwt_rules import JWTAuthenticationRules
from .model_managers import ModelManager


def authenticate(
    auth_classes: list = None,
    rule_name: Optional[str] = None,
    token_type: str = "access",
    assign_to_request: bool = False,
    assignment_key: str = "instance",
    model_id_key_name: str = "id",
    return_func: Callable = make_response,
    return_func_args: Tuple[Any, ...] = ({"error": "Unauthorized access"}, 401),
    jwt_rules: Optional[JWTAuthenticationRules] = None,
) -> Callable:
    """Decorator that protects a Flask route with JWT authentication.

    At least one authentication class in ``auth_classes`` must successfully
    authenticate the request for the view to be called.

    Args:
        auth_classes: List of :class:`BaseAuthentication` subclass **classes**
            (not instances) to try in order. If any succeeds, the route is called.
        rule_name: JWT rule name (None -> default rule).
        token_type: Expected token type ('access' or 'refresh').
        assign_to_request: If True, attaches the authenticated model instance to
            ``request.<assignment_key>``.
        assignment_key: The attribute name on the request object (default 'instance').
        model_id_key_name: The primary key field name on the model (default 'id').
        return_func: Callable invoked on auth failure (default: ``make_response``).
        return_func_args: Arguments passed to ``return_func`` on failure.
        jwt_rules: Override for the JWTAuthenticationRules singleton (for testing).

    Returns:
        The decorated view function or a failure response.

    Raises:
        TypeError: If auth_classes, return_func, or return_func_args are invalid types.
    """
    # Default to AuthenticateJWT if no classes provided
    if auth_classes is None:
        from .authentication_classes import AuthenticateJWT
        auth_classes = [AuthenticateJWT]

    # Validate arguments at decoration time
    if not callable(return_func):
        raise TypeError("return_func must be a callable.")
    if not isinstance(return_func_args, tuple):
        raise TypeError("return_func_args must be a tuple.")
    if not isinstance(auth_classes, list) or not all(
        (isinstance(auth, type) and issubclass(auth, BaseAuthentication))
        for auth in auth_classes
    ):
        raise TypeError(
            "auth_classes must be a list of BaseAuthentication subclass classes (not instances)."
        )

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not auth_classes:
                return return_func(*return_func_args)

            active_rules = jwt_rules if jwt_rules is not None else JWTAuthenticationRules()
            token_header: str = active_rules.get_token_header(rule_name)

            for auth_class in auth_classes:
                auth_instance: BaseAuthentication = auth_class(
                    token_header, token_type, rule_name
                )
                payload: Optional[dict[str, Any]] = auth_instance.authenticate_request(request)
                if payload:
                    if assign_to_request:
                        instance = _get_instance(rule_name, payload, model_id_key_name, active_rules)
                        setattr(request, assignment_key, instance)
                    return view(*args, **kwargs)

            # None of the auth_classes authenticated the request
            return return_func(*return_func_args)

        return wrapper

    return decorator


def _get_instance(
    rule_name: Optional[str],
    payload: dict[str, Any],
    model_id_key_name: str = "id",
    jwt_rules: Optional[JWTAuthenticationRules] = None,
    model_manager: Optional[ModelManager] = None,
) -> Any:
    """Retrieve the model instance identified by the JWT payload."""
    if jwt_rules is None:
        jwt_rules = JWTAuthenticationRules()
    if model_manager is None:
        model_manager = ModelManager()

    table_class = model_manager.get_model(jwt_rules.get_table_path(rule_name))
    id_key_name: str = f"{table_class.__tablename__}_{model_id_key_name}"
    instance_id = payload.get(id_key_name)
    return model_manager.get_instance(table_class, **{model_id_key_name: instance_id})
