from fastapi import APIRouter, HTTPException

from backend.core.engine_loader import load_engine
from backend.schemas.search_schema import SearchRequest, ExplainRequest


router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/")
def search_repositories(request: SearchRequest):
    try:
        engine = load_engine()

        results = engine.search(
            query=request.query,
            top_k=request.top_k,
            candidate_pool=request.candidate_pool,
            language=request.language,
            license_name=request.license_name,
            min_stars=request.min_stars,
            topic=request.topic,
        )

        return {
            "query": request.query,
            "count": len(results),
            "results": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain")
def explain_result(request: ExplainRequest):
    try:
        engine = load_engine()

        explanation = engine.explain_result(
            query=request.query,
            repo_identifier=request.repo_identifier,
        )

        return explanation

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))