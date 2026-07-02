from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.history_service import record_search_history
from backend.core.semantic_loader import (
    explain_result,
    hybrid_search,
    profile_from_payload,
)
from backend.core.user_service import preferences_to_profile_dict
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.search_schema import ExplainRequest, SearchRequest
from backend.security.deps import get_optional_current_user

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/")
def search_repositories(
    request: SearchRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    try:
        payload = request.model_dump()

        if current_user and not payload.get("profile"):
            db_profile = preferences_to_profile_dict(db, current_user)
            if db_profile:
                payload["profile"] = db_profile

        results = hybrid_search(payload)
        response = {
            "query": request.query,
            "count": len(results),
            "engine": "semantic_hybrid_recommender",
            "results": results,
        }

        if current_user:
            record_search_history(
                db,
                current_user,
                request.query,
                "hybrid",
                len(results),
            )

        return response

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
