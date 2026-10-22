from __future__ import annotations
"""
Module contains convenience helper functions for token refresh, logout, and cleanup.
"""

from typing import Optional, Any, Dict
from .factory import TokenFactory
from .blacklist_token import BlackListed
from .exceptions import TokenInvalid, TokenBlacklisted, TokenTypeMismatch


def refresh_access_token(
    refresh_token: str,
    rule_name: Optional[str] = None,
    extra_payload: Optional[Dict[str, Any]] = None,
) -> str:
    """Validate a refresh token and issue a new access token.

    Args:
        refresh_token: The signed JWT refresh token string.
        rule_name: The JWT rule name (None -> default rule).
        extra_payload: Optional extra dictionary fields to embed in the new access token.

    Returns:
        A newly minted signed access token string.

    Raises:
        TokenBlacklisted: If the refresh token has been revoked.
        TokenInvalid: If the refresh token signature is invalid or expired.
        TokenTypeMismatch: If the provided token is not a refresh token.
    """
    factory = TokenFactory()
    bl = BlackListed()

    # 1. Check blacklist
    if bl.is_blacklisted(rule_name, refresh_token):
        raise TokenBlacklisted("The provided refresh token has been blacklisted/revoked.")

    # 2. Validate token
    payload = factory.validate_token(refresh_token, rule_name=rule_name)
    if payload is None:
        raise TokenInvalid("The provided refresh token is invalid or has expired.")

    # 3. Check token type
    if payload.get("type") != "refresh":
        raise TokenTypeMismatch(f"Expected token type 'refresh', got '{payload.get('type')}'.")

    # 4. Extract instance_id if table tracking was used
    rule_handler = factory.rule_handler
    instance_id = None
    if rule_handler.get_table(rule_name):
        table_path = rule_handler.get_table_path(rule_name)
        model_class = factory.manager.get_model(table_path)
        table_name = model_class.__tablename__
        instance_id = payload.get(f"{table_name}_id")

    # 5. Issue new access token
    return factory.generate_token(
        rule_name=rule_name,
        instance_id=instance_id,
        extra_payload=extra_payload or {},
    )


def logout(
    token: str,
    rule_name: Optional[str] = None,
    remove_from_track: bool = True,
    **extra_fields: Any,
) -> None:
    """Revoke a token by adding it to the blacklist table.

    Args:
        token: The JWT string to revoke.
        rule_name: The JWT rule name (None -> default rule).
        remove_from_track: Whether to also remove the token record from the track model.
        **extra_fields: Additional fields to store on the blacklist database record.
    """
    BlackListed().blacklist(
        rule_name=rule_name,
        token=token,
        extra_blacklist_fields=extra_fields,
        remove_token_from_track_model=remove_from_track,
    )
