from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.rag_advisor import (
    explain_repo_with_rag,
    generate_roadmap_with_rag,
)


router = APIRouter(prefix="/api/rag", tags=["RAG Advisor"])


class RagRepoRequest(BaseModel):
    repo: Dict[str, Any]
    query: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None


@router.post("/explain")
def explain_repo(request: RagRepoRequest):
    return explain_repo_with_rag(
        repo=request.repo,
        query=request.query,
        profile=request.profile,
    )


@router.post("/roadmap")
def roadmap_repo(request: RagRepoRequest):
    return generate_roadmap_with_rag(
        repo=request.repo,
        query=request.query,
        profile=request.profile,
    )