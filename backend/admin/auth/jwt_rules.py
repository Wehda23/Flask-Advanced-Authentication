"""
Module that contains JWT_AUTHENTICATION RULES
"""

from typing import Any, Type, Optional, NoReturn, Union
from .exceptions import (
    InvalidDefaultKeyType,
    JWTRulesEmpty,
    DefaultRuleDoesNotExist,
    InvalidJWTRule,
    JWTFieldValueError,
)
from pydantic import ValidationError, BaseModel
from .validator import check_validator_class


class JWTAuthenticationRules:
    """Class that contains JWT_AUTHENTICATION rules with Singleton design pattern."""

    _instance: Type["JWTAuthenticationRules"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "JWTAuthenticationRules":
        if cls._instance is None:
            cls._instance = super(JWTAuthenticationRules, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        rules: dict[str, dict[str, Any]] = None,
        defualt_rule: str = "default",
        rule_validator: Optional[BaseModel] = None,
    ) -> None:
        """Constructor"""
        if not hasattr(self, "_initialized"):  # Initialize only once
            self.rule_validator = rule_validator
            self.rules = rules
            self.default_rule = defualt_rule
            self._initialized = True

    @property
    def rule_validator(self) -> Type["BaseModel"]:
        """
        Rule Validator getter
        """
        return self._rule_validator

    @rule_validator.setter
    def rule_validator(self, value: Optional[BaseModel]) -> None:
        """
        Setter Method for rule_validator
        """
        # Allowing None values to pass validation
        if value is not None:
            # Check if value is a subclasss of BaseModel
            if not check_validator_class(value):
                raise TypeError(
                    "rule_validator must be a subclass of Pydantic BaseModel"
                )
        self._rule_validator: Optional[BaseModel] = value

    @property
    def rules(self) -> dict[str, dict[str, Any]]:
        """Rules getter"""
        return self._rules

    @rules.setter
    def rules(self, value: dict[str, dict[str, Any]]) -> None:
        """Rules setter"""
        # Check if value is a dictionary
        if not isinstance(value, dict):
            raise TypeError(f"rules must be a dictionary, not {type(value)}")
        # Validate rules
        if self.rule_validator:
            self._rules = self.validate_rules(value)
            return
        # Assign Rules
        self._rules: dict[str, dict[str, Any]] = value

    def validate_rules(
        self, rules: dict[str, dict[str, Any]]
    ) -> Union[dict[dict[str, Any]], NoReturn]:
        """
        Validate rules

        Args:
            rules (dict): Dictionary containing different jwt rules

        Raises:
            TypeError: In case if a rule is not a dictionary
            InvalidJWTRule: In case if rule is missing required fields\
                or required fields are with wrong data-type.

        Raises error such that will look as following:
        ```py
        {
            "example_rule": [
            ]
            "second_rule": [
            ]
            ...
        }
        ```

        Returns:
            Updated Rules with defaults for none specified fields.
        """
        # Declare list of validaton errors
        errors: dict[str, list[dict[str, Any]]] = {}
        # Rules
        updated_rules: dict[str, dict[str, Any]] = {}

        for key, rule in rules.items():
            if not isinstance(rule, dict):
                raise TypeError(f"rule ({key}) must be a dictionary, not {type(rule)}")
            try:
                # Declare validator
                rule_validator: Type["BaseModel"] = self.rule_validator(**rule)
                # Update rule with defaults added to it.
                updated_rules[key] = rule_validator.model_dump()
            except ValidationError as e:
                # Add error to errors list
                errors[key] = e.errors()

        # Check if errors Raise InvalidJWTRule
        if errors:
            raise InvalidJWTRule(errors)

        # Return Updated Rules
        return updated_rules

    @property
    def default_rule(self) -> str:
        """
        Method to grab property default_rule
        """
        return self._default_rule

    @default_rule.setter
    def default_rule(self, value: str) -> None:
        """
        Setter Method for default_rule
        """
        # Check if value is not None
        if not isinstance(value, str):
            raise InvalidDefaultKeyType(
                f"Default Key should be of type string you entered type({type(value)})"
            )

        # Check if rules is already setup
        if not hasattr(self, "rules"):
            raise JWTRulesEmpty("Class rules attribute is empty")

        # Check if the key exists within rules
        if value not in self.rules:
            raise DefaultRuleDoesNotExist(
                "Default class rule key does not exist within the specified JWT_AUTHENTICATION_RULES."
            )

        self._default_rule: str = value

    def get_rule(
        self, rule: Optional[str], *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Method to retrieve a JWT rule

        Args:
            rule (Optional[str]): Return JWT Rule settings (default: returns the default rule in case rule is None)

        Returns:
            dict: JWT Rule Settings.
        """
        if rule is None:
            return self.default_rule
        return self.rules.get(rule, *args, **kwargs)

    def disallow_none(value: Any, error_message, *args: Any, **kwargs) -> Any:
        """
        Method used to disallow a field to be None Value

        Args:
            value (Any): Value to be compared to None
            error_message (str): Error message to be raised when value is None
            *args: Any
            **kwargs: Any

        Raises:
            JWTFieldValueError: <error_message>

        Returns:
            Any: value
        """
        if value is None:
            raise JWTFieldValueError(error_message)
        return value

    def get_secret_key(
        self, rule_name: Optional[str], key_name: str = "secret_key"
    ) -> str:
        """Method used to get secret key from rule."""
        # Check Rule name
        if rule_name is None:
            rule_name: str = self.default_rule
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return secret key
        return self.disallow_none(
            rule.get(key_name),
            f"""
            Secret Key for rule {rule_name} is not defined.

            JWT_AUTHENTICATION_RULES = {{
                ...,
                "{rule_name}": {{
                    ...,
                    "secret_key": "SECRET_KEY", # Please make sure to define it as is.
                    ...
                }},
                ...
            }}
            """,
        )

    def get_algorithm(
        self, rule_name: Optional[str], key_name: str = "algorithm"
    ) -> str:
        """Method used to get algorithm from rule."""
        # Check Rule name
        if rule_name is None:
            rule_name: str = self.default_rule
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return algorithm
        return self.disallow_none(
            rule.get(key_name),
            f"""
            JWT Algorithm for rule {rule_name} is not defined.

            JWT_AUTHENTICATION_RULES = {{
                ...,
                "{rule_name}": {{
                    ...,
                    "algorithm": "HS256", # Please make sure to define it as is.
                    ...
                }},
                ...
            }}
            """,
        )

    def get_token_lifetime(
        self, rule_name: Optional[str], token_type: str = "access"
    ) -> Any:
        """Method used to get token lifetime from rule."""
        # Check Rule name
        if rule_name is None:
            rule_name: str = self.default_rule
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return token lifetime
        return self.disallow_none(
            rule.get(f"{token_type}_expires_in"),
            f"""
            Token lifetime for {token_type} token is not defined in rule {rule_name}.
            from datetime import timedelta

            JWT_AUTHENTICATION_RULES = {{
                ...,
                "{rule_name}": {{
                    ...,
                    "{token_type}_token_lifetime": timedelta(minutes=30), # Please make sure to define it as is.
                    ...
                }},
                ...
            }}
            """,
        )

    def get_access_lifetime(
        self, rule_name: Optional[str], key_name: str = "access_expires_in"
    ) -> Any:
        """Method used to get access lifetime from rule."""
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return access lifetime
        return rule.get(key_name)

    def get_refresh_lifetime(
        self, rule_name: Optional[str], key_name: str = "refresh_expires_in"
    ) -> Any:
        """Method used to get refresh lifetime from rule."""
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return refresh lifetime
        return rule.get(key_name)

    def get_table(self, rule_name: Optional[str], key_name: str = "table") -> bool:
        """Method used to get table from rule."""
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return table
        return rule.get(key_name)

    def get_table_path(
        self, rule_name: Optional[str], key_name: str = "table_path"
    ) -> str:
        """
        Method used to get table path from rule.

        Args:
            rule_name (str): Name of the required rule.
            key_name (str): Name of the key to get. Defaults to "table_path"

        Raises:
            JWTFieldValueError: In case the model path field is not specified in token rule.

        Returns:
            str: Path to the token rule as in "package.path.path2.ModelClass"
        """
        # Check Rule name
        if rule_name is None:
            rule_name: str = self.default_rule
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return algorithm
        return self.disallow_none(
            rule.get(key_name),
            f"""
            {rule_name} rule does not have {key_name}.

            JWT_AUTHENTICATION_RULES = {{
                ...,
                "{rule_name}": {{
                    ...,
                    "table": True, # Table field was True and path to the model was not provided.
                    "table_path": "your_project.path.ModelClass", # This is how to provide path to the model.
                    ...
                }},
                ...
            }}
            """,
        )

    def get_token_header(
        self, rule_name: Optional[str], key_name: str = "token_header"
    ) -> str:
        """
        Method used to get token headers from rule.

        Args:
            rule_name (str): Name of the required rule.
            key_name (str): Name of the key to get. Defaults to "token_header"

        Raises:
            JWTFieldValueError: In case the token header is None

        Returns:
            str: token headers as in "Bearer "
        """
        # Check Rule name
        if rule_name is None:
            rule_name: str = self.default_rule
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return algorithm
        return self.disallow_none(
            rule.get(key_name),
            f"""
            {rule_name} rule does not have {key_name}.

            JWT_AUTHENTICATION_RULES = {{
                ...,
                "{rule_name}": {{
                    ...,
                    "token_header": "Bearer ", # Please make sure to define it as is.
                    ...
                }},
                ...
            }}
            """,
        )

    def get_track_created(
        self, rule_name: Optional[str], key_name: str = "track_created"
    ) -> bool:
        """Method used to get track created from rule."""
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return track created
        return rule.get(key_name)

    def get_track_created_table_path(
        self, rule_name: Optional[str], key_name: str = "track_created_table_path"
    ) -> str:
        """
        Method used to get track created table path from rule.

        Args:
            rule_name (str): Name of the required rule.
            key_name (str): Name of the key to get. Defaults to "track_created_table_path"

        Raises:
            JWTFieldValueError: In case the model path field is not specified in token rule.

        Returns:
            str: Path to the token rule as in "package.path.path2.ModelClass"
        """
        # Check Rule name
        if rule_name is None:
            rule_name: str = self.default_rule
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return algorithm
        return self.disallow_none(
            rule.get(key_name),
            f"""
            {rule_name} rule does not have {key_name}.

            JWT_AUTHENTICATION_RULES = {{
                ...,
                "{rule_name}": {{
                    ...,
                    "track_created": True, # track created tokens field was True and path to the model was not provided.
                    "track_created_table_path": "your_project.path.TrackModelClass", # This is how to provide path to the model.
                    ...
                }},
                ...
            }}
            """,
        )

    def get_track_created_allow_duplicates(
        self, rule_name: Optional[str], key_name: str = "track_created_allow_duplicates"
    ) -> bool:
        """Method used to get track created allow duplicates from rule."""
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return track created allow duplicates
        return rule.get(key_name)

    def get_blacklisted(
        self, rule_name: Optional[str], key_name: str = "blacklisted"
    ) -> bool:
        """Method used to get blacklisted from rule."""
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return blacklisted
        return rule.get(key_name)

    def get_blacklisted_tabled_path(
        self, rule_name: Optional[str], key_name: str = "blacklisted_table_path"
    ) -> str:
        """
        Method used to get blacklisted table path from rule.

        Args:
            rule_name (str): Name of the required rule.
            key_name (str): Name of the key to get. Defaults to "blacklisted_table_path"

        Raises:
            JWTFieldValueError: In case the model path field is not specified in token rule.

        Returns:
            str: Path to the token rule as in "package.path.path2.ModelClass"
        """
        # Check Rule name
        if rule_name is None:
            rule_name: str = self.default_rule
        # First of all acquire the rule
        rule: dict[str, Any] = self.get_rule(rule_name)
        # Return algorithm
        return self.disallow_none(
            rule.get(key_name),
            f"""
            {rule_name} rule does not have {key_name}.

            JWT_AUTHENTICATION_RULES = {{
                ...,
                "{rule_name}": {{
                    ...,
                    "blacklisted": True, # blacklisted field was True and path to the model was not provided.
                    "blacklisted_table_path": "your_project.path.BlackListedTokens", # This is how to provide path to the model.
                    ...
                }},
                ...
            }}
            """,
        )
