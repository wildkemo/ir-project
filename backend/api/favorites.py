"""Favorites API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.history_service import add_favorite, list_favorites, remove_favorite
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.auth_schema import MessageResponse
from backend.schemas.history_schema import FavoriteRequest, FavoriteResponse
from backend.security.deps import get_current_active_user

router = APIRouter(prefix="/users/favorites", tags=["Favorites"])


@router.get("", response_model=list[FavoriteResponse])
def get_favorites(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return list_favorites(db, current_user)


@router.post("", response_model=FavoriteResponse, status_code=201)
def create_favorite(
    payload: FavoriteRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return add_favorite(db, current_user, payload.repo_identifier)


@router.delete("/{repo_identifier:path}", response_model=MessageResponse)
def delete_favorite(
    repo_identifier: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    from backend.core.validators import sanitize_repo_identifier

    try:
        cleaned = sanitize_repo_identifier(repo_identifier)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not remove_favorite(db, current_user, cleaned):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
    return MessageResponse(message="Favorite removed")
