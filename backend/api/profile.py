from fastapi import APIRouter, HTTPException

from backend.core.profile_loader import (
    get_profile_questions_payload,
    recommend_for_profile,
    search_with_profile,
)
from backend.schemas.profile_schema import ProfileRecommendRequest, ProfileSearchRequest


router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/questions")
def get_profile_questions():
    try:
        return get_profile_questions_payload()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
def profile_recommend(request: ProfileRecommendRequest):
    try:
        payload = request.model_dump()
        results = recommend_for_profile(payload)
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
