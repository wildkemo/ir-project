"""User preferences API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.user_service import get_user_preferences, update_user_preferences
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.preferences_schema import UserPreferencesRequest, UserPreferencesResponse
from backend.security.deps import get_current_active_user

router = APIRouter(prefix="/users/preferences", tags=["Preferences"])


@router.get("", response_model=UserPreferencesResponse)
def read_preferences(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return get_user_preferences(db, current_user)


@router.put("", response_model=UserPreferencesResponse)
def save_preferences(
    payload: UserPreferencesRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return update_user_preferences(db, current_user, payload)
