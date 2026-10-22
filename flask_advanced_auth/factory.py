from __future__ import annotations
"""
Module contains TokenFactory — the central class for generating and validating JWTs.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from .jwt_rules import JWTAuthenticationRules
from .TokenProxy import PyJWT
from .model_managers import ModelManager


class TokenFactoryInterface(ABC):
    """Abstract interface for token factory classes."""

    @abstractmethod
    def generate_token(self, *args: Any, **kwargs: Any) -> str:
        """Generate an access token."""
        pass

    @abstractmethod
    def generate_refresh_token(self, *args: Any, **kwargs: Any) -> str:
        """Generate a refresh token."""
        pass

    @abstractmethod
    def validate_token(self, *args: Any, **kwargs: Any) -> Any:
        """Validate a token."""
        pass


class TokenFactory(TokenFactoryInterface):
    """Generates, encodes, decodes, and tracks JWT access and refresh tokens."""

    def __init__(
        self,
        rule_handler: Optional[JWTAuthenticationRules] = None,
        token_proxy: Optional[PyJWT] = None,
        manager: Optional[ModelManager] = None,
    ) -> None:
        self._rule_handler = rule_handler
        self._token_proxy = token_proxy
        self._manager = manager

    @property
    def rule_handler(self) -> JWTAuthenticationRules:
        if self._rule_handler is not None:
            return self._rule_handler
        return JWTAuthenticationRules()

    @rule_handler.setter
    def rule_handler(self, value: JWTAuthenticationRules) -> None:
        self._rule_handler = value

    @property
    def token_proxy(self) -> PyJWT:
        if self._token_proxy is not None:
            return self._token_proxy
        return PyJWT()

    @token_proxy.setter
    def token_proxy(self, value: PyJWT) -> None:
        self._token_proxy = value

    @property
    def manager(self) -> ModelManager:
        if self._manager is None:
            self._manager = ModelManager()
        return self._manager

    @manager.setter
    def manager(self, value: ModelManager) -> None:
        self._manager = value

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
        """Generate a signed JWT access token."""
        token_type: str = "access"
        token: str = self.create_token(
            token_type=token_type,
            rule_name=rule_name,
            instance_id=instance_id,
            extra_payload=extra_payload,
            include_rule_name=include_rule_name,
            ignore_model_instance_existance=ignore_model_instance_existance,
            *args,
            **kwargs,
        )
        if self.rule_handler.get_track_created(rule_name):
            self.track_token(
                rule_name=rule_name,
                token=token,
                instance_id=instance_id,
                token_type=token_type,
                additional_track_token_fields=additional_track_token_fields,
            )
        return token

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
        """Generate a signed JWT refresh token."""
        token_type: str = "refresh"
        token: str = self.create_token(
            token_type=token_type,
            rule_name=rule_name,
            instance_id=instance_id,
            extra_payload=extra_payload,
            include_rule_name=include_rule_name,
            ignore_model_instance_existance=ignore_model_instance_existance,
            *args,
            **kwargs,
        )
        if self.rule_handler.get_track_created(rule_name):
            self.track_token(
                rule_name=rule_name,
                token=token,
                instance_id=instance_id,
                token_type=token_type,
                additional_track_token_fields=additional_track_token_fields,
            )
        return token

    def validate_token(
        self,
        token: str,
        rule_name: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Decode and verify a JWT token."""
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
        """Build and sign a JWT token."""
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

    def decode_token(self, token: str, secret_key: str, algorithm: str, *args: Any, **kwargs: Any) -> Any:
        """Proxy to PyJWT decode."""
        return self.token_proxy.decode_token(
            token=token, secret_key=secret_key, algorithm=algorithm, *args, **kwargs
        )

    def encode_token(self, payload: dict, secret_key: str, algorithm: str, *args: Any, **kwargs: Any) -> str:
        """Proxy to PyJWT encode."""
        return self.token_proxy.encode_token(
            payload=payload, secret_key=secret_key, algorithm=algorithm, *args, **kwargs
        )

    def instance_id_payload(
        self,
        rule_name: str,
        instance_id: Any,
        ignore_model_instance_existance: bool,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build the instance_id fragment of the JWT payload."""
        if instance_id is None:
            raise ValueError("instance_id cannot be None when table=True is configured.")

        table_path: str = self.rule_handler.get_table_path(rule_name)
        model_class = self.manager.get_model(table_path)
        table_name: str = model_class.__tablename__

        if not ignore_model_instance_existance:
            if not self.manager.get_instance(model_class, id=instance_id):
                raise ValueError(
                    f"Instance {instance_id} does not exist in '{table_name}' table."
                )

        return {f"{table_name}_id": instance_id}

    def track_token(
        self,
        rule_name: str,
        token: str,
        instance_id: Any,
        token_type: str,
        additional_track_token_fields: dict,
    ) -> None:
        """Persist a token record to the rule's track model table."""
        track_table_path: str = self.rule_handler.get_track_created_table_path(rule_name)
        TrackModel = self.manager.get_model(track_table_path)

        allow_duplicates: bool = self.rule_handler.get_track_created_allow_duplicates(rule_name)
        if not allow_duplicates and self.manager.get_instance(TrackModel, instance_id=instance_id):
            raise ValueError(f"Token already exists for instance_id={instance_id}.")

        new_instance = TrackModel(
            token=token,
            instance_id=instance_id,
            token_type=token_type,
            **additional_track_token_fields,
        )
        self.manager.register(new_instance)

    def check_extra_payload(self, extra_payload: dict = {}, *args: Any, **kwargs: Any) -> dict:
        """Validate that extra_payload is a dictionary."""
        if not isinstance(extra_payload, dict):
            raise ValueError("extra_payload must be a dictionary.")
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
        """Assemble the full JWT payload dict."""
        payload: dict[str, Any] = self.token_proxy.required_payload(rule_name, token_type)

        if self.rule_handler.get_table(rule_name):
            payload.update(
                self.instance_id_payload(
                    rule_name, instance_id, ignore_model_instance_existance
                )
            )

        if include_rule_name:
            payload["rule_name"] = rule_name

        if extra_payload:
            payload.update(self.check_extra_payload(extra_payload))

        return payload
