"""
Module contains authentication decorator
"""

from functools import wraps
from flask import request, make_response, Response
from typing import Any, Callable, Tuple, Union, Type
from .authentication_classes import BaseAuthentication
from .jwt_rules import JWTAuthenticationRules
from .model_managers import ModelManager


def authenticate(
    auth_classes: list[BaseAuthentication],
    rule_name: str = None,
    token_type: str = "access",
    assign_to_request: bool = False,
    assigment_key: str = "instance",
    model_id_key_name: str = "id",
    return_func: Callable = make_response,
    return_func_args: Tuple[Any] = ({"error": "Unauthorized access"}, 401),
    jwt_rules: JWTAuthenticationRules = JWTAuthenticationRules(),
    *args: Any,
    **kwargs: Any,
) -> Union[Callable, Response]:
    """
    A decorator that checks if the request meets all specified authentications

    Args:
        auth_classess (list[Authentication]): A list of authentication classes
        rule_name (str, optional): The name of the rule. Defaults to None.
        token_type (str, optional): The type of token. Defaults to 'access'.
        assign_to_request (bool, optional): Whether to assign the authentication instance to the request. Defaults to False.
        assigment_key (str, optional): The key to assign the authentication instance to the request (setattr(request, "instance")). Defaults to "instance"\
            you can call request.instance and you will get the related model instance.
        model_id_key_name (str): if the key of the id model is different you can change here for lookup.
        return_func (Callable, optional): The function to return when authentication fails. Defaults to make_response
        return_func_args (Tuple[Any], optional): The arguments to pass to the return function. Defaults
        to ({"error": "Unauthorized access"}, 401)


    Returns:
        Callable: The decorated route function in case of success.
        Response: A 401 Unauthorized response in case of failure.
    """
    # Validate return_func to be a callable
    if not callable(return_func):
        raise TypeError("return_func must be a callable")
    # Validate return_fun_args should be a tuple
    if not isinstance(return_func_args, tuple):
        raise TypeError("return_func_args must be a tuple")
    # Validate auth_classes should be a list of BaseAuthentication instances
    if not isinstance(auth_classes, list) or not all(
        isinstance(auth, BaseAuthentication) for auth in auth_classes
    ):
        raise TypeError("auth_classes must be a list of BaseAuthentication instances")

    # Grab token headers
    token_header: str = jwt_rules.get_token_header(rule_name)

    # Decorator
    def decorator(view: Callable) -> Union[Callable, Response]:
        @wraps(view)
        def wrapper(*args: Any, **kwargs: Any):
            # Check if auth_classes is empty
            if not auth_classes:
                return return_func(*return_func_args)
            # Check if request is authenticated
            for auth in auth_classes:
                # Initiate class
                auth_instance: Type["BaseAuthentication"] = auth(
                    token_header, token_type, rule_name
                )
                # Check if request is authenticated
                payload: Union[dict[str, Any], None] = (
                    auth_instance.authenticate_request(request)
                )
                if payload:
                    if assign_to_request:
                        instance = get_instance(rule_name, payload, model_id_key_name)
                        setattr(request, assigment_key, instance)
                    return view(*args, **kwargs)
                else:
                    return return_func(*return_func_args)
            return wrapper

        return wrapper

    return decorator


# Helper function for the decorator
def get_instance(
    rule_name: str,
    payload: dict[str, Any],
    model_id_key_name: str = "id",
    jwt_rules: JWTAuthenticationRules = JWTAuthenticationRules(),
    model_manager: ModelManager = ModelManager(),
) -> None:
    """
    gets an instance of a model to the request object.

    Args:
        rule_name (str, optional): The name of the rule. Defaults to None.
        payload (dict[str, Any], optional): The payload of the JWT token. Defaults to
        model_id_key_name (str, optional): The key name of the model id in the payload
        jwt_rules (JWTAuthenticationRules, optional): JWT rules. Defaults to JWTAuthenticationRules().
        model_manager (ModelManager, optional): The model manager. Defaults to ModelManager().
    """
    table_class = model_manager.get_model(jwt_rules.get_table_path(rule_name))
    id_key_name: str = f"{table_class.__tablename__}_{model_id_key_name}"
    instance_id: Any = {model_id_key_name: payload.get(id_key_name)}
    instance = model_manager.get_instance(table_class, **instance_id)
    return instance
