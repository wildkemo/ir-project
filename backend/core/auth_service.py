"""Authentication business logic."""

import logging
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from backend.database.config import get_access_token_expire_minutes
from backend.models.refresh_token import RefreshToken
from backend.models.role import Role
from backend.models.user import User
from backend.models.user_preference import UserPreference
from backend.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse
from backend.security.jwt import (
    create_access_token,
    create_refresh_token_value,
    get_refresh_token_expiry,
    hash_refresh_token,
)
from backend.security.password import hash_password, verify_password

logger = logging.getLogger(__name__)


def _get_default_role(db: Session) -> Role:
    role = db.query(Role).filter(Role.name == "User").first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role not configured. Run seed script.",
        )
    return role


def register_user(db: Session, payload: RegisterRequest) -> User:
    """Create a new user account."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    role = _get_default_role(db)
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role_id=role.id,
    )
    db.add(user)
    db.flush()

    db.add(UserPreference(user_id=user.id))
    db.commit()
    db.refresh(user)

    logger.info("User registered", extra={"user_id": str(user.id), "username": user.username})
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    """Validate credentials and return the user."""
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.email == payload.email)
        .first()
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def issue_tokens(db: Session, user: User) -> TokenResponse:
    """Create access and refresh tokens for a user."""
    access_token = create_access_token(user.id, {"role": user.role.name})
    refresh_value = create_refresh_token_value()
    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_value),
        expires_at=get_refresh_token_expiry(),
    )
    db.add(refresh_record)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_value,
        expires_in=get_access_token_expire_minutes() * 60,
    )


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse:
    """Rotate refresh token and issue new access token."""
    token_hash = hash_refresh_token(refresh_token)
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash, RefreshToken.revoked.is_(False))
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    now = datetime.now(timezone.utc)
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        record.revoked = True
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == record.user_id)
        .first()
    )
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    record.revoked = True
    return issue_tokens(db, user)


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    """Revoke a refresh token on logout."""
    token_hash = hash_refresh_token(refresh_token)
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if record:
        record.revoked = True
        db.commit()
        logger.info("Refresh token revoked", extra={"user_id": str(record.user_id)})
