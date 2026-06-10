from fastapi import APIRouter
from backend.schemas.project_explainer import ProjectExplainRequest
from backend.core.project_explainer import explain_project

router = APIRouter(prefix="/api/project-explainer", tags=["Project Explainer"])


@router.post("/explain")
def explain_project_endpoint(request: ProjectExplainRequest):
    """
    Explains one selected repository in detail.

    This endpoint is designed to power a frontend button like:
    "Explain Project" / "Summarize Repo" / "Understand without opening GitHub".
    """
    return explain_project(
        repo_data=request.repo,
        profile=request.profile,
        query=request.query,
    )
