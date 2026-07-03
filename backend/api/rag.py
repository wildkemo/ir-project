import os
import time
from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.ai_tracking import repo_identifier_from_payload, track_ai_request
from backend.core.rag_advisor import (
    chat_about_repo,
    explain_repo_with_rag,
    generate_roadmap_with_rag,
)
from backend.database.session import get_db
from backend.models.user import User
from backend.security.deps import get_optional_current_user

router = APIRouter(prefix="/api/rag", tags=["RAG Advisor"])


class RagRepoRequest(BaseModel):
    repo: Dict[str, Any]
    query: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None


class RagChatRequest(BaseModel):
    repo: Dict[str, Any]
    message: str
    profile: Optional[Dict[str, Any]] = None
    history: list[Dict[str, str]] = []


@router.post("/explain")
def explain_repo(
    request: RagRepoRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    return track_ai_request(
        db,
        current_user,
        "rag_explain",
        repo_identifier_from_payload(request.repo),
        lambda: explain_repo_with_rag(
            repo=request.repo,
            query=request.query,
            profile=request.profile,
        ),
        model=os.getenv("OLLAMA_MODEL"),
    )


@router.post("/roadmap")
def roadmap_repo(
    request: RagRepoRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    return track_ai_request(
        db,
        current_user,
        "learning_roadmap",
        repo_identifier_from_payload(request.repo),
        lambda: generate_roadmap_with_rag(
            repo=request.repo,
            query=request.query,
            profile=request.profile,
        ),
        model=os.getenv("OLLAMA_MODEL"),
    )


@router.post("/chat")
def chat_repo(
    request: RagChatRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    return track_ai_request(
        db,
        current_user,
        "rag_explain",
        repo_identifier_from_payload(request.repo),
        lambda: chat_about_repo(
            repo=request.repo,
            message=request.message,
            profile=request.profile,
            history=request.history,
        ),
        model=os.getenv("OLLAMA_MODEL"),
    )