from fastapi import APIRouter, HTTPException

from backend.core.engine_loader import load_engine
from backend.schemas.search_schema import RecommendRequest


router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.post("/")
def recommend_repositories(request: RecommendRequest):
    try:
        engine = load_engine()

        results = engine.recommend_similar(
            repo_identifier=request.repo_identifier,
            top_k=request.top_k,
            same_language_only=request.same_language_only,
        )

        return {
            "repo_identifier": request.repo_identifier,
            "count": len(results),
            "results": results,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))