"""Authentication API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from backend.core.rate_limit import limiter
from sqlalchemy.orm import Session, joinedload

from backend.core.auth_service import (
    authenticate_user,
    issue_tokens,
    refresh_access_token,
    register_user,
    revoke_refresh_token,
)
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.auth_schema import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from backend.security.deps import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("10/minute")
def register(
    request: Request,
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    user = register_user(db, payload)
    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user.id)
        .first()
    )
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
def login(
    request: Request,
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    user = authenticate_user(db, payload)
    return issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
def refresh(
    request: Request,
    payload: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
):
    return refresh_access_token(db, payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
def logout(
    payload: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
):
    revoke_refresh_token(db, payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
