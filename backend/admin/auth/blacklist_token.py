"""
Module contains class to blacklist tokens based on rule name and settings
"""

from abc import ABC, abstractmethod
from .jwt_rules import JWTAuthenticationRules
from .model_managers import ModelManager
from typing import Any, Union


class AbstractBlackList(ABC):
    """
    Abstract class to blacklist tokens based on rule name and settings
    """

    __rule_handler = None
    """
    Rule handler to get rule settings
    """
    __manager = None
    """
    Manager to handle database related operations to store blacklisted tokens
    """

    @abstractmethod
    def blacklist(self, rule_name: str, token: str) -> None:
        """
        Blacklist token based on rule name and settings

        :param rule_name: Name of the rule
        :param token: Token to blacklist
        """
        pass

    @abstractmethod
    def is_blacklisted(self, rule_name: str, token: str) -> bool:
        """
        Check if token is blacklisted

        :param rule_name: Name of the rule
        :param token: Token to check

        :return: True if token is blacklisted, False otherwise
        """
        pass


class BlackListed(AbstractBlackList):
    """
    Class to blacklist tokens based on rule name and settings
    """

    __rule_handler: JWTAuthenticationRules = JWTAuthenticationRules()
    __manager: ModelManager = ModelManager()

    def blacklist_token(
        self,
        rule_name: str,
        token: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Blacklist token based on rule name and settings

        :param rule_name: Name of the rule
        :param token: Token to blacklist
        :param model_path_key: Key to get model path
        """
        # Get model path
        model_path: str = self.__rule_handler.get_blacklisted_tabled_path(rule_name)
        # Get model instance
        BlackListModel = self.__manager.get_model(model_path=model_path)
        # Add token to blacklisted tokens
        model_instance = BlackListModel(token=token, **kwargs)
        # register token to blacklist
        self.__manager.register(model_instance)

    def unregister_token_from_track_model(
        self,
        rule_name: str,
        token: str,
    ) -> None:
        """
        Unregister token from track model

        :param rule_name: Name of the rule
        :param token: Token to unregister
        """
        # Get model path
        model_path: str = self.__rule_handler.get_track_created_table_path(rule_name)
        # Get model instance
        model_instance = self.__manager.get_instance(model_path=model_path, token=token)
        if model_instance:
            # Unregister token from track model
            self.__manager.unregister(model_instance)

    def blacklist(
        self,
        rule_name: str,
        token: str,
        extra_blacklist_fields: dict = {},
        remove_token_from_track_model: bool = False,
    ) -> None:
        """
        Blacklist token based on rule name and settings

        :param rule_name: Name of the rule
        :param token: Token to blacklist
        :param remove_token_from_track_model: Remove token from track model, Unregister the token
        :param extra_blacklist_fields: Extra fields for BlackListModel
        """
        # Perform Black List token operations
        self.blacklist_token(rule_name=rule_name, token=token, **extra_blacklist_fields)

        # Unregister the token from track model
        if remove_token_from_track_model:
            self.unregister_token_from_track_model(rule_name, token)

    def is_blacklisted(self, rule_name: str, token: str) -> Union[Any, None]:
        """
        Check if token is blacklisted

        :param rule_name: Name of the rule, Needed to check on which blacklist model is this token might exist
        :param token: Token to check

        :return: True if token is blacklisted, False otherwise
        """
        # If the model is not black for blacklist
        if not self.__rule_handler.get_blacklisted():
            return False
        # Get model path
        model_path: str = self.__rule_handler.get_blacklisted_tabled_path(rule_name)
        # get black listed token
        blacklisted_token = self.__manager.get_instance(
            model_path=model_path, token=token
        )
        return blacklisted_token
