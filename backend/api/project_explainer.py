from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.ai_tracking import repo_identifier_from_payload, track_ai_request
from backend.core.project_explainer import explain_project
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.project_explainer import ProjectExplainRequest
from backend.security.deps import get_optional_current_user

router = APIRouter(prefix="/api/project-explainer", tags=["Project Explainer"])


@router.post("/explain")
def explain_project_endpoint(
    request: ProjectExplainRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """
    Explains one selected repository in detail.

    This endpoint is designed to power a frontend button like:
    "Explain Project" / "Summarize Repo" / "Understand without opening GitHub".
    """
    return track_ai_request(
        db,
        current_user,
        "explain_repository",
        repo_identifier_from_payload(request.repo),
        lambda: explain_project(
            repo_data=request.repo,
            profile=request.profile,
            query=request.query,
        ),
    )
