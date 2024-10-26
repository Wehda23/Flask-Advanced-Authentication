"""
Module contains rule validator
"""

from typing import Any, Optional, NoReturn
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator
from datetime import timedelta


# Pydantic Validation
class JWTRuleDetails(BaseModel):
    """JWT Token Rules."""

    # Configuration for Pydantic V2
    model_config = ConfigDict(
        extra="allow",  # Forbid extra fields not defined in the model
        validate_default=True,  # Ensure default values are validated
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
    # Include Model Related JWT
    table: Optional[bool] = Field(False, alias=AliasChoices("TABEL", "tabel", "Tabel"))
    table_path: Optional[str] = Field(
        None, alias=AliasChoices("TABEL_PATH", "tabel_path", "TabelPath")
    )
    token_header: Optional[str] = Field(
        "Bearer ", alias=AliasChoices("TOKEN_HEADER", "token_header", "TokenHeader")
    )
    # Include Track Created JWT
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
    # Inlcude blacklisted jwt
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
    def ensure_timedelta(cls, value):
        if value and not isinstance(value, timedelta):
            raise ValueError(f"{value} is not a valid timedelta object")
        return value

    @field_validator("token_header")
    def ensure_token_header(cls, value: str) -> str:
        if value.replace(" ", "") == "":
            raise ValueError(f"{value} is not a valid token header")
        return value


# Check Validator Class
def check_validator_class(validator_class: type) -> bool:
    """
    Checks if the given validator class is a subclass of BaseModel

    :param validator_class: Class to check

    :return: True if it is a subclass of BaseModel, False otherwise
    """
    if issubclass(validator_class, BaseModel):
        return True
    return False
