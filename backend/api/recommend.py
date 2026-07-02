from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.history_service import record_recommendation_history
from backend.core.semantic_loader import recommend_similar
from backend.schemas.search_schema import RecommendRequest
from backend.database.session import get_db
from backend.models.user import User
from backend.security.deps import get_optional_current_user

router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.post("/")
def recommend_similar_repositories(
    request: RecommendRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """Similar repos via semantic embeddings (semantic_hybrid_recommender)."""
    try:
        results = recommend_similar(
            repo_identifier=request.repo_identifier,
            top_k=request.top_k,
            same_language_only=request.same_language_only,
        )

        if current_user:
            for item in results:
                repo_id = item.get("full_name") or item.get("title")
                if repo_id:
                    record_recommendation_history(
                        db,
                        current_user,
                        repo_id,
                        item.get("semantic_cosine") or item.get("similarity"),
                        "similar_repository",
                    )

        return {
            "repo_identifier": request.repo_identifier,
            "count": len(results),
            "engine": "semantic_hybrid_recommender",
            "results": results,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
