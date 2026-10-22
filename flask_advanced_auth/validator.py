from __future__ import annotations
"""
Module contains rule validator for JWT authentication rules.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator
from datetime import timedelta


class JWTRuleDetails(BaseModel):
    """Pydantic validator for JWT token rule configuration dictionaries.

    Supports case-insensitive and multi-alias configuration keys.

    Example:
        >>> rule = {
        ...     "description": "User auth token",
        ...     "secret_key": "mysecret",
        ...     "algorithm": "HS256",
        ...     "access_token_lifetime": timedelta(minutes=30),
        ... }
        >>> validated = JWTRuleDetails(**rule)
    """

    model_config = ConfigDict(
        extra="allow",
        validate_default=True,
        populate_by_name=True,
    )

    description: str = Field(
        ..., alias=AliasChoices("DESCRIPTION", "description", "Description")
    )
    access_expires_in: timedelta = Field(
        ...,
        alias=AliasChoices(
            "ACCESS_TOKEN_LIFETIME", "access_token_lifetime", "AccessTokenLifetime"
        ),
    )
    refresh_expires_in: Optional[timedelta] = Field(
        None,
        alias=AliasChoices(
            "REFRESH_TOKEN_LIFETIME", "refresh_token_lifetime", "RefreshTokenLifetime"
        ),
    )
    algorithm: str = Field(
        ..., alias=AliasChoices("ALGORITHM", "algorithm", "Algorithm")
    )
    secret_key: str = Field(
        ..., alias=AliasChoices("SECRET_KEY", "secret_key", "SecretKey")
    )
    # FIX T-02: corrected typos "tabel" -> "table" in all aliases
    table: Optional[bool] = Field(
        False, alias=AliasChoices("TABLE", "table", "Table")
    )
    table_path: Optional[str] = Field(
        None, alias=AliasChoices("TABLE_PATH", "table_path", "TablePath")
    )
    token_header: Optional[str] = Field(
        "Bearer ", alias=AliasChoices("TOKEN_HEADER", "token_header", "TokenHeader")
    )
    track_created: Optional[bool] = Field(
        False, alias=AliasChoices("TRACK_CREATED", "track_created", "TrackCreated")
    )
    track_created_table_path: Optional[str] = Field(
        None,
        alias=AliasChoices(
            "TRACK_CREATED_TABLE_PATH",
            "track_created_table_path",
            "TrackCreatedTablePath",
        ),
    )
    track_created_allow_duplicates: Optional[bool] = Field(
        True,
        alias=AliasChoices(
            "TRACK_CREATED_ALLOW_DUPLICATES",
            "track_created_allow_duplicates",
            "TrackCreatedAllowDuplicates",
        ),
    )
    blacklisted: Optional[bool] = Field(
        False,
        alias=AliasChoices("BLACKLISTED", "blacklisted", "BlackListed", "Blacklisted"),
    )
    blacklisted_table_path: Optional[str] = Field(
        None,
        alias=AliasChoices(
            "BLACKLISTED_TABLE_PATH",
            "blacklisted_table_path",
            "BlackListedTablePath",
            "BlacklistedTablePath",
        ),
    )

    @field_validator("access_expires_in", "refresh_expires_in")
    @classmethod
    def ensure_timedelta(cls, value: Optional[timedelta]) -> Optional[timedelta]:
        """Validate that the value is a timedelta instance."""
        if value is not None and not isinstance(value, timedelta):
            raise ValueError(f"{value!r} is not a valid timedelta object")
        return value

    @field_validator("token_header")
    @classmethod
    def ensure_token_header(cls, value: str) -> str:
        """Validate that the token header is not blank."""
        if value.replace(" ", "") == "":
            raise ValueError(f"{value!r} is not a valid token header")
        return value


def check_validator_class(validator_class: type) -> bool:
    """Check if the given class is a subclass of Pydantic BaseModel.

    Args:
        validator_class: The class to check.

    Returns:
        True if it is a subclass of BaseModel, False otherwise.
    """
    try:
        return issubclass(validator_class, BaseModel)
    except TypeError:
        return False
