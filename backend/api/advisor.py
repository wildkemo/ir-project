from __future__ import annotations

from fastapi import APIRouter

from backend.core.ai_advisor import advise
from backend.core.repo_comparator import compare_repos
from backend.core.repo_explainer import explain_repo
from backend.core.roadmap_generator import generate_roadmap
from backend.schemas.advisor import (
    AdvisorSummaryRequest,
    CompareReposRequest,
    ExplainRepoRequest,
    RoadmapRequest,
)

router = APIRouter(prefix="/api/advisor", tags=["AI Advisor"])


@router.post("/explain")
def explain(request: ExplainRepoRequest):
    """
    Explain one selected repository.
    Frontend can pass the repo object directly from search results or repo details.
    """
    return explain_repo(
        repo=request.repo,
        profile=request.profile,
        query=request.query,
        score_breakdown=request.score_breakdown,
        include_roadmap=request.include_roadmap,
    )


@router.post("/roadmap")
def roadmap(request: RoadmapRequest):
    """
    Generate a personalized roadmap for a selected repository.
    """
    return generate_roadmap(repo=request.repo, profile=request.profile)


@router.post("/compare")
def compare(request: CompareReposRequest):
    """
    Compare two selected repositories side by side.
    """
    return compare_repos(
        repo_a=request.repo_a,
        repo_b=request.repo_b,
        profile=request.profile,
        query=request.query,
    )


@router.post("/summary")
def summary(request: AdvisorSummaryRequest):
    """
    Build advisor summary from top search/recommendation results.
    """
    return advise(
        query=request.query,
        profile=request.profile,
        results=request.results,
        top_k=request.top_k,
    )
