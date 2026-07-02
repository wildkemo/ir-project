from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.history_service import record_recommendation_history
from backend.core.profile_loader import (
    get_profile_questions_payload,
    recommend_for_profile,
    search_with_profile,
)
from backend.core.user_service import preferences_to_profile_dict
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.profile_schema import ProfileRecommendRequest, ProfileSearchRequest
from backend.security.deps import get_optional_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])


def _merge_profile_payload(db: Session, payload: dict, current_user: User | None) -> dict:
    if current_user and not any(v for k, v in payload.items() if k != "top_k" and v is not None):
        db_profile = preferences_to_profile_dict(db, current_user)
        if db_profile:
            payload.update(db_profile)
    return payload


@router.get("/questions")
def get_profile_questions():
    try:
        return get_profile_questions_payload()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
def profile_recommend(
    request: ProfileRecommendRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    try:
        payload = _merge_profile_payload(db, request.model_dump(), current_user)
        results = recommend_for_profile(payload)

        if current_user:
            for item in results[:10]:
                repo_id = item.get("full_name") or item.get("title")
                if repo_id:
                    reason = "; ".join(item.get("why_recommended", [])[:3]) or None
                    record_recommendation_history(
                        db,
                        current_user,
                        repo_id,
                        item.get("score"),
                        reason,
                    )

        return {
            "count": len(results),
            "engine": "smart_profile_recommender_v2",
            "profile": {
                k: v
                for k, v in payload.items()
                if k != "top_k" and v is not None
            },
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
def profile_search(request: ProfileSearchRequest):
    try:
        payload = request.model_dump()
        results = search_with_profile(payload)
        return {
            "query": request.query,
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
