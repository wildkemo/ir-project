"""User profile API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from backend.core.user_service import update_user_profile
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.auth_schema import UserResponse
from backend.schemas.user_schema import UserUpdateRequest
from backend.security.deps import get_current_active_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me", response_model=UserResponse)
def update_profile(
    payload: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    user = update_user_profile(db, current_user, payload)
    return (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user.id)
        .first()
    )
