"""
Model contains factory design pattern classes to handle generating tokens for rules
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from .jwt_rules import JWTAuthenticationRules
from .TokenProxy import PyJWT
from .model_managers import ModelManager


class TokenFactoryInterface(ABC):
    """Interface for token factory classes"""

    rule_handler = None
    """Rule handler instance"""
    token_proxy = None
    """
    Class used to encode and decode JWT tokens
    """
    manager = None
    """
    Manager instance to store tokens
    """

    # Access Token Methods
    @abstractmethod
    def generate_token(self, *args: Any, **kwargs: Any) -> str:
        """Generate a token for the given user data"""
        pass

    # Refresh Token Methods
    @abstractmethod
    def generate_refresh_token(self, *args: Any, **kwargs: Any) -> str:
        """Generate a refresh token for the given user data"""
        pass

    @abstractmethod
    def validate_token(self, *args: Any, **kwargs: Any) -> bool:
        """Validate a token for the given user data"""
        pass


class TokenFactory(TokenFactoryInterface):
    """Abstract class for token factory"""

    rule_handler: JWTAuthenticationRules = JWTAuthenticationRules()

    token_proxy: PyJWT = PyJWT()

    manager: ModelManager = ModelManager()

    # Access token
    def generate_token(
        self,
        rule_name: Optional[str] = None,
        instance_id: Any = None,
        extra_payload: dict = {},
        include_rule_name: bool = False,
        ignore_model_instance_existance: bool = True,
        additional_track_token_fields: dict = {},
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        Generate access token based on the provided data.

        Note that providing a rule_name as a None will result in using the default rule.

        :param rule_name: Name of the rule to be used for token generation (default: Will use default rule)
        :param instance_id: ID of the instance to be used for token generation (default: None)
        :param extra_payload: Extra payload to be included in the token (default: {})
        :param include_rule_name: True if want to add rule name to the payload (default: False)
        :param ignore_model_instance_existance: Ignore checking model instance existance in Database (default: False)
        :param additional_track_token_fields: Additional fields for track token creation table (default: {})

        :return: Token generated
        """
        # Declare token type
        token_type: str = "access"
        # Generate the token
        token: str = self.create_token(
            type=token_type,
            rule_name=rule_name,
            instance_id=instance_id,
            extra_payload=extra_payload,
            include_rule_name=include_rule_name,
            ignore_model_instance_existance=ignore_model_instance_existance,
            *args,
            **kwargs,
        )
        # Model actions if rule is related to a table.
        if self.rule_handler.get_track_created(rule_name):
            self.track_token(
                rule_name=rule_name,
                token=token,
                instance_id=instance_id,
                token_type=token_type,
                additional_track_token_fields=additional_track_token_fields,
            )
        # Return the Token
        return token

    # Refresh Token Methods
    def generate_refresh_token(
        self,
        rule_name: Optional[str] = None,
        instance_id: Any = None,
        extra_payload: dict = {},
        include_rule_name: bool = False,
        ignore_model_instance_existance: bool = True,
        additional_track_token_fields: dict = {},
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        Generate refresh token based on the provided data.

        Note that providing a rule_name as a None will result in using the default rule.

        :param rule_name: Name of the rule to be used for token generation (default: Will use default rule)
        :param instance_id: ID of the instance to be used for token generation (default: None)
        :param extra_payload: Extra payload to be included in the token (default: {})
        :param include_rule_name: True if want to add rule name to the payload (default: False)
        :param ignore_model_instance_existance: Ignore checking model instance existance in Database (default: False)
        :param additional_track_token_fields: Additional fields for track token creation table (default: {})
        :param args: Any additional arguments
        :param kwargs: Any additional keyword arguments

        :return: Token generated
        """
        # Declare token type
        token_type: str = "refresh"
        # Generate the token
        token: str = self.create_token(
            type=token_type,
            rule_name=rule_name,
            instance_id=instance_id,
            extra_payload=extra_payload,
            include_rule_name=include_rule_name,
            ignore_model_instance_existance=ignore_model_instance_existance,
            *args,
            **kwargs,
        )
        # Model actions if rule is related to a table.
        if self.rule_handler.get_track_created(rule_name):
            self.track_token(
                rule_name=rule_name,
                token=token,
                instance_id=instance_id,
                token_type=token_type,
                additional_track_token_fields=additional_track_token_fields,
            )
        # Return the Token
        return token

    def validate_token(
        self,
        token: str,
        rule_name: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Validate token based on the provided token

        Returns:
            dict: Incase token validation pass otherwise None
        """
        return self.decode_token(
            token,
            secret_key=self.rule_handler.get_secret_key(rule_name=rule_name),
            algorithm=self.rule_handler.get_algorithm(rule_name=rule_name),
            *args,
            **kwargs,
        )

    def create_token(
        self,
        token_type: str = "access",
        rule_name: Optional[str] = None,
        instance_id: Any = None,
        extra_payload: dict = {},
        include_rule_name: bool = False,
        ignore_model_instance_existance: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        Method used to create token.

        Args:
            token_type (str): Type of the token (default: "access")
            rule_name (str): Rule name to be included in payload
            instance_id (Any): Instance ID to be included in payload
            extra_payload (dict): Extra payload to be included in payload
            include_rule_name (bool): Flag to include rule name in payload
            ignore_model_instance_existance (bool): Flag to ignore model instance existence

        Returns:
            str: Encoded token
        """
        payload: dict[str, Any] = self.build_payload(
            token_type=token_type,
            rule_name=rule_name,
            instance_id=instance_id,
            extra_payload=extra_payload,
            include_rule_name=include_rule_name,
            ignore_model_instance_existance=ignore_model_instance_existance,
        )

        return self.encode_token(
            payload=payload,
            secret_key=self.rule_handler.get_secret_key(rule_name),
            algorithm=self.rule_handler.get_algorithm(rule_name),
            *args,
            **kwargs,
        )

    # Token Proxy Related Section
    def decode_token(
        self, token: str, secret_key: str, algorithm: str, *args, **kwargs
    ) -> Any:
        """Decode the token"""
        return self.token_proxy.decode_token(
            token=token, secret_key=secret_key, algorithm=algorithm, *args, **kwargs
        )

    def encode_token(
        self,
        payload: dict,
        secret_key: str,
        algorithm: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        Method used to encode token
        Args:
        payload (dict): Payload to be encoded
        secret_key (str): Secret key to be used for encoding
        algorithm (str): Algorithm to be used for encoding
        Returns:
        str: Encoded token
        """
        return self.token_proxy.encode_token(
            payload=payload,
            secret_key=secret_key,
            algorithm=algorithm,
            *args,
            **kwargs,
        )

    # Database Related Section
    def instance_id_payload(
        self,
        rule_name: str,
        instance_id: Any,
        ignore_model_instance_existance: bool,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Method used to perform actions on the model

        Args:
            rule (str): Name of the rule
            instance_id (Any): ID of the instance.

        Raises:
            ValueError: Incase of instance id is None\
                Rule is None or Rule is not type dictionary\
                In case table_path is None

        Returns:
            dict: Payload for the JWT token
        """

        # Check instance_id
        if instance_id is None:
            raise ValueError("Instance ID cannot be None")

        # Grab Table path
        table_path: str = self.rule_handler.get_track_created_table_path(rule_name)

        # Grab model
        model_class = self.manager.get_model(table_path)

        # Parse Table name
        table_name: str = model_class.__tablename__

        # Check instance existance in model table
        if not ignore_model_instance_existance:
            if not self.manager.get_instance(model_class, id=instance_id):
                raise ValueError(
                    f"Instance {instance_id} does not exist in {table_name} table"
                )

        return {
            f"{table_name}_id": instance_id,
        }

    def track_token(
        self,
        rule_name: str,
        token: str,
        instance_id: Any,
        token_type: str,
        additional_track_token_fields: dict,
    ) -> None:
        """
        Method used to track the token

        Args:
            rule_name (str): Name of the rule
            token (str): JWT token
            instance_id (Any): Instance ID
            token_type (str): Type of token
            additional_track_token_fields (dict): Additional fields to track
        """
        # Get table name
        track_table_path: str = self.rule_handler.get_track_created_table_path(
            rule_name
        )

        TrackModel = self.manager.get_model(track_table_path)
        # Check Duplicates Allowed or not
        allow_duplicates: bool = self.rule_handler.get_track_created_allow_duplicates(
            rule_name
        )
        if not allow_duplicates and self.manager.get_instance(
            TrackModel, instance_id=instance_id
        ):
            raise ValueError("Token already exists for the instance ID")
        # Create new instance
        new_instance = TrackModel(
            token=token,
            instance_id=instance_id,
            token_type=token_type,
            **additional_track_token_fields,
        )
        self.manager.register(new_instance)

    # Payload Related Section
    def check_extra_payload(
        self, extra_payload: dict = {}, *args: Any, **kwargs: Any
    ) -> None:
        """
        Method used to check extra payload

        Raises:
            ValueError: Incase extra payload is not a dictionary.

        Returns:
            dict: Validated Extra Payload.
        """
        # Check if extra_payload is a dictionary
        if not isinstance(extra_payload, dict):
            raise ValueError("Extra payload must be a dictionary")
        return extra_payload

    def build_payload(
        self,
        token_type: str = "access",
        rule_name: Optional[str] = None,
        instance_id: Any = None,
        extra_payload: dict = {},
        include_rule_name: bool = False,
        ignore_model_instance_existance: bool = True,
    ) -> dict[str, Any]:
        """
        Method used to build payload

        Args:
            rule_name (str): Rule name to be included in payload
            instance_id (Any): Instance id to be included in payload
            extra_payload (dict): Extra payload to be included in payload
            include_rule_name (bool): Flag to include rule name in payload
            ignore_model_instance_existance (bool): Flag to ignore model instance existence

        Returns:
            dict: Payload
        """
        # Then generate the token
        payload: dict[str, Any] = self.token_proxy.required_payload(
            rule_name, token_type
        )
        # If table_jwt is True, add the instance_id to the payload
        if self.rule_handler.get_table(rule_name):
            payload.update(
                self.instance_id_payload(
                    rule_name, instance_id, ignore_model_instance_existance
                )
            )
        # If include_rule_name is true include it in Json Web Token Payload
        if include_rule_name:
            payload["rule_name"] = rule_name
        # Add Extra_payload
        if extra_payload:
            payload.update(self.check_extra_payload(extra_payload))
        # Return Payload
        return payload
