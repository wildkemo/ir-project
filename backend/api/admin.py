"""Admin-only API routes for platform management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.models.ai_request import AIRequest
from backend.models.recommendation_history import RecommendationHistory
from backend.models.search_history import SearchHistory
from backend.models.user import User
from backend.schemas.admin_schema import (
    AdminAILogsResponse,
    AdminAnalyticsResponse,
    AdminStatsResponse,
    AdminUserListResponse,
    TopSearchQuery,
)
from backend.schemas.history_schema import AIRequestResponse
from backend.database.session import get_db
from backend.security.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    return AdminStatsResponse(
        total_users=db.query(User).count(),
        total_searches=db.query(SearchHistory).count(),
        total_recommendations=db.query(RecommendationHistory).count(),
        total_ai_requests=db.query(AIRequest).count(),
        ollama_connected=False,
        qdrant_connected=False,
    )


@router.get("/analytics", response_model=AdminAnalyticsResponse)
def admin_analytics(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    top_rows = (
        db.query(SearchHistory.query, func.count(SearchHistory.id).label("count"))
        .group_by(SearchHistory.query)
        .order_by(func.count(SearchHistory.id).desc())
        .limit(10)
        .all()
    )

    ai_type_rows = (
        db.query(AIRequest.request_type, func.count(AIRequest.id).label("count"))
        .group_by(AIRequest.request_type)
        .all()
    )

    return AdminAnalyticsResponse(
        top_search_queries=[
            TopSearchQuery(query=row.query, count=row.count) for row in top_rows
        ],
        total_searches=db.query(SearchHistory).count(),
        total_recommendations=db.query(RecommendationHistory).count(),
        total_ai_requests=db.query(AIRequest).count(),
        ai_request_types={row.request_type: row.count for row in ai_type_rows},
    )


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=100, ge=1, le=500),
):
    users = (
        db.query(User)
        .options(joinedload(User.role))
        .order_by(User.created_at.desc())
        .limit(limit)
        .all()
    )
    return AdminUserListResponse(users=users, count=len(users))


@router.get("/ai-logs", response_model=AdminAILogsResponse)
def list_ai_logs(
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=500),
):
    logs = (
        db.query(AIRequest)
        .order_by(AIRequest.created_at.desc())
        .limit(limit)
        .all()
    )
    return AdminAILogsResponse(
        logs=[AIRequestResponse.model_validate(log) for log in logs],
        count=len(logs),
    )
