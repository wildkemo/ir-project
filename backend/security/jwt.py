"""JWT token creation and validation."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from backend.database.config import (
    get_access_token_expire_minutes,
    get_jwt_algorithm,
    get_jwt_secret,
    get_refresh_token_expire_days,
)


def create_access_token(subject: uuid.UUID, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a short-lived JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=get_access_token_expire_minutes())
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, get_jwt_secret(), algorithm=get_jwt_algorithm())


def create_refresh_token_value() -> str:
    """Generate a cryptographically secure refresh token string."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token for secure storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    return jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])


def get_refresh_token_expiry() -> datetime:
    """Return the expiry datetime for a new refresh token."""
    return datetime.now(timezone.utc) + timedelta(days=get_refresh_token_expire_days())
