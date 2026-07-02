"""User history API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.history_service import (
    list_ai_requests,
    list_recommendation_history,
    list_search_history,
)
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.history_schema import (
    AIRequestResponse,
    RecommendationHistoryResponse,
    SearchHistoryResponse,
)
from backend.security.deps import get_current_active_user

router = APIRouter(prefix="/users/history", tags=["History"])


@router.get("/search", response_model=list[SearchHistoryResponse])
def get_search_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
):
    return list_search_history(db, current_user, limit)


@router.get("/recommendations", response_model=list[RecommendationHistoryResponse])
def get_recommendation_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
):
    return list_recommendation_history(db, current_user, limit)


@router.get("/ai", response_model=list[AIRequestResponse])
def get_ai_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=200),
):
    return list_ai_requests(db, current_user, limit)
