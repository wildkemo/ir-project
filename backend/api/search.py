from fastapi import APIRouter, HTTPException

from backend.core.semantic_loader import (
    explain_result,
    hybrid_search,
    profile_from_payload,
)
from backend.schemas.search_schema import SearchRequest, ExplainRequest


router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/")
def search_repositories(request: SearchRequest):
    try:
        payload = request.model_dump()
        results = hybrid_search(payload)

        return {
            "query": request.query,
            "count": len(results),
            "engine": "semantic_hybrid_recommender",
            "results": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
def explain_search_result(request: ExplainRequest):
    try:
        profile = profile_from_payload(
            request.profile.model_dump() if request.profile else None
        )

        return explain_result(
            query=request.query,
            repo_identifier=request.repo_identifier,
            profile=profile,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
