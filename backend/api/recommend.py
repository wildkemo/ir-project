from fastapi import APIRouter, HTTPException

from backend.core.semantic_loader import load_semantic_hybrid
from backend.schemas.search_schema import RecommendRequest


router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.post("/")
def recommend_similar_repositories(request: RecommendRequest):
    """Similar repos via semantic embeddings (semantic_hybrid_recommender)."""
    try:
        hybrid = load_semantic_hybrid()

        results = hybrid.recommend_similar(
            repo_identifier=request.repo_identifier,
            top_k=request.top_k,
            same_language_only=request.same_language_only,
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
