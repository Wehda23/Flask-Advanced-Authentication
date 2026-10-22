from __future__ import annotations
"""
Module contains BlackListed class for token revocation.
"""

from abc import ABC, abstractmethod
from .jwt_rules import JWTAuthenticationRules
from .model_managers import ModelManager
from typing import Any, Union, Optional


class AbstractBlackList(ABC):
    """Abstract interface for token blacklisting."""

    @abstractmethod
    def blacklist(self, rule_name: str, token: str) -> None:
        """Add a token to the blacklist."""
        pass

    @abstractmethod
    def is_blacklisted(self, rule_name: str, token: str) -> bool:
        """Check whether a token is blacklisted."""
        pass


class BlackListed(AbstractBlackList):
    """Blacklist manager that persists revoked tokens in a database table."""

    def __init__(
        self,
        rule_handler: Optional[JWTAuthenticationRules] = None,
        manager: Optional[ModelManager] = None,
    ) -> None:
        self.__rule_handler = rule_handler
        self.__manager = manager

    @property
    def _rule_handler(self) -> JWTAuthenticationRules:
        if self.__rule_handler is not None:
            return self.__rule_handler
        return JWTAuthenticationRules()

    @_rule_handler.setter
    def _rule_handler(self, value: JWTAuthenticationRules) -> None:
        self.__rule_handler = value

    @property
    def _manager(self) -> ModelManager:
        if self.__manager is None:
            self.__manager = ModelManager()
        return self.__manager

    @_manager.setter
    def _manager(self, value: ModelManager) -> None:
        self.__manager = value

    def blacklist_token(
        self,
        rule_name: str,
        token: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Persist a token to the rule's blacklist table."""
        model_path: str = self._rule_handler.get_blacklisted_table_path(rule_name)
        BlackListModel = self._manager.get_model(model_path=model_path)
        model_instance = BlackListModel(token=token, **kwargs)
        self._manager.register(model_instance)

    def unregister_token_from_track_model(
        self,
        rule_name: str,
        token: str,
    ) -> None:
        """Remove a token record from the rule's token-tracking table."""
        model_path: str = self._rule_handler.get_track_created_table_path(rule_name)
        model_instance = self._manager.get_instance(model_path=model_path, token=token)
        if model_instance:
            self._manager.unregister(model_instance)

    def blacklist(
        self,
        rule_name: str,
        token: str,
        extra_blacklist_fields: dict = {},
        remove_token_from_track_model: bool = False,
    ) -> None:
        """Blacklist a token and optionally remove it from the tracking table."""
        self.blacklist_token(rule_name=rule_name, token=token, **extra_blacklist_fields)
        if remove_token_from_track_model:
            self.unregister_token_from_track_model(rule_name, token)

    def is_blacklisted(self, rule_name: str, token: str) -> Union[Any, None]:
        """Check whether a token is in the blacklist."""
        if not self._rule_handler.get_blacklisted(rule_name):
            return False
        model_path: str = self._rule_handler.get_blacklisted_table_path(rule_name)
        blacklisted_token = self._manager.get_instance(
            model_path=model_path, token=token
        )
        return blacklisted_token
