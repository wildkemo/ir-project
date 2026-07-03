from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.ai_advisor import advise
from backend.core.ai_tracking import repo_identifier_from_payload, track_ai_request
from backend.core.repo_comparator import compare_repos
from backend.core.repo_explainer import answer_repo_question, explain_repo, _format_steps_roadmap
from backend.core.repo_intelligence import get_repo_name
from backend.core.roadmap_generator import generate_roadmap
from backend.core.rag_advisor import chat_about_repo
from backend.database.session import get_db
from backend.models.user import User
from backend.schemas.advisor import (
    AdvisorChatRequest,
    AdvisorSummaryRequest,
    CompareReposRequest,
    ExplainRepoRequest,
    RoadmapRequest,
)
from backend.security.deps import get_optional_current_user

router = APIRouter(prefix="/api/advisor", tags=["AI Advisor"])


@router.post("/explain")
def explain(
    request: ExplainRepoRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """
    Explain one selected repository.
    Frontend can pass the repo object directly from search results or repo details.
    """
    return track_ai_request(
        db,
        current_user,
        "explain_repository",
        repo_identifier_from_payload(request.repo),
        lambda: explain_repo(
            repo=request.repo,
            profile=request.profile,
            query=request.query,
            score_breakdown=request.score_breakdown,
            include_roadmap=request.include_roadmap,
        ),
        user_message=request.query,
    )


@router.post("/roadmap")
def roadmap(
    request: RoadmapRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """
    Generate a personalized roadmap for a selected repository.
    """
    def _run():
        roadmap = generate_roadmap(
            repo=request.repo,
            profile=request.profile,
            query=request.query,
        )
        repo_name = get_repo_name(request.repo)
        return {
            **roadmap,
            "mode": "rule_based",
            "repo_name": repo_name,
            "answer": (
                f"Here is a personalized roadmap for **{repo_name}**:\n\n"
                f"{_format_steps_roadmap(roadmap)}"
            ),
        }

    return track_ai_request(
        db,
        current_user,
        "learning_roadmap",
        repo_identifier_from_payload(request.repo),
        _run,
        user_message=request.query,
    )


@router.post("/chat")
def chat(
    request: AdvisorChatRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """
    Conversational Q&A about the selected repository.
    Uses Ollama when available; falls back to rule-based query-aware answers.
    """
    history = [{"role": m.role, "content": m.content} for m in request.history]

    def _run():
        try:
            return chat_about_repo(
                repo=request.repo,
                message=request.message,
                profile=request.profile,
                history=history,
            )
        except Exception:
            return answer_repo_question(
                repo=request.repo,
                message=request.message,
                profile=request.profile,
                history=history,
            )

    return track_ai_request(
        db,
        current_user,
        "ai_chat",
        repo_identifier_from_payload(request.repo),
        _run,
        user_message=request.message,
    )


@router.post("/compare")
def compare(
    request: CompareReposRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """
    Compare two selected repositories side by side.
    """
    return track_ai_request(
        db,
        current_user,
        "compare_repositories",
        repo_identifier_from_payload(request.repo_a),
        lambda: compare_repos(
            repo_a=request.repo_a,
            repo_b=request.repo_b,
            profile=request.profile,
            query=request.query,
        ),
        user_message=request.query,
    )


@router.post("/summary")
def summary(
    request: AdvisorSummaryRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_current_user)] = None,
):
    """
    Build advisor summary from top search/recommendation results.
    """
    return track_ai_request(
        db,
        current_user,
        "repository_summary",
        repo_identifier_from_payload(request.results[0]) if request.results else None,
        lambda: advise(
            query=request.query,
            profile=request.profile,
            results=request.results,
            top_k=request.top_k,
        ),
        user_message=request.query,
    )
