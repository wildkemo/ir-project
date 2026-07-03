"""History and favorites tracking services."""

from sqlalchemy.orm import Session

from backend.models.ai_request import AIRequest
from backend.models.favorite_repository import FavoriteRepository
from backend.models.recommendation_history import RecommendationHistory
from backend.models.search_history import SearchHistory
from backend.models.user import User


def add_favorite(db: Session, user: User, repo_identifier: str) -> FavoriteRepository:
    """Save a repository favorite."""
    existing = (
        db.query(FavoriteRepository)
        .filter(
            FavoriteRepository.user_id == user.id,
            FavoriteRepository.repo_identifier == repo_identifier,
        )
        .first()
    )
    if existing:
        return existing

    favorite = FavoriteRepository(user_id=user.id, repo_identifier=repo_identifier)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user: User, repo_identifier: str) -> bool:
    """Remove a repository favorite. Returns True if deleted."""
    favorite = (
        db.query(FavoriteRepository)
        .filter(
            FavoriteRepository.user_id == user.id,
            FavoriteRepository.repo_identifier == repo_identifier,
        )
        .first()
    )
    if favorite is None:
        return False
    db.delete(favorite)
    db.commit()
    return True


def list_favorites(db: Session, user: User) -> list[FavoriteRepository]:
    """List user favorites ordered by most recent."""
    return (
        db.query(FavoriteRepository)
        .filter(FavoriteRepository.user_id == user.id)
        .order_by(FavoriteRepository.created_at.desc())
        .all()
    )


def record_search_history(
    db: Session,
    user: User,
    query: str,
    search_type: str,
    result_count: int,
) -> None:
    """Record a search history entry."""
    db.add(
        SearchHistory(
            user_id=user.id,
            query=query,
            search_type=search_type,
            result_count=result_count,
        )
    )
    db.commit()


def record_recommendation_history(
    db: Session,
    user: User,
    repo_identifier: str,
    score: float | None,
    reason: str | None,
) -> None:
    """Record a recommendation history entry."""
    db.add(
        RecommendationHistory(
            user_id=user.id,
            repo_identifier=repo_identifier,
            recommendation_score=score,
            recommendation_reason=reason,
        )
    )
    db.commit()


def record_ai_request(
    db: Session,
    user: User,
    request_type: str,
    repo_identifier: str | None,
    model: str | None,
    latency_ms: float | None,
    user_message: str | None = None,
    ai_response: str | None = None,
    response_mode: str | None = None,
) -> None:
    """Record an AI feature usage entry with optional prompt and response content."""
    db.add(
        AIRequest(
            user_id=user.id,
            request_type=request_type,
            repo_identifier=repo_identifier,
            model=model,
            latency_ms=latency_ms,
            user_message=user_message,
            ai_response=ai_response,
            response_mode=response_mode,
        )
    )
    db.commit()


def list_search_history(db: Session, user: User, limit: int = 50) -> list[SearchHistory]:
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def list_recommendation_history(
    db: Session, user: User, limit: int = 50
) -> list[RecommendationHistory]:
    return (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == user.id)
        .order_by(RecommendationHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def list_ai_requests(db: Session, user: User, limit: int = 50) -> list[AIRequest]:
    return (
        db.query(AIRequest)
        .filter(AIRequest.user_id == user.id)
        .order_by(AIRequest.created_at.desc())
        .limit(limit)
        .all()
    )
