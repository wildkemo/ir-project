"""
Repo Explainer for OpenSeek.

Explains one repository using metadata, README-derived features, score breakdown,
and user profile. This is the "Understand this repo" feature.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.core.repo_intelligence import (
    enrich_repo,
    get_repo_name,
    get_repo_url,
    profile_language_match,
)
from backend.core.roadmap_generator import generate_roadmap


def build_summary(repo: Dict[str, Any]) -> str:
    repo = enrich_repo(repo)
    name = get_repo_name(repo)
    description = repo.get("description") or "No description is available in the dataset"
    language = repo.get("language") or "an unspecified language"
    topics = repo.get("topics") or []
    tech_stack = repo.get("tech_stack") or []

    topic_text = ", ".join(topics[:4]) if topics else "general software development"
    tech_text = ", ".join(tech_stack[:5]) if tech_stack else language

    return (
        f"{name} is a {language}-based repository related to {topic_text}. "
        f"Its description says: {description}. "
        f"Detected technologies or signals include: {tech_text}."
    )


def detect_best_for(repo: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> str:
    repo = enrich_repo(repo)
    goal = str((profile or {}).get("goal") or "").lower()
    intents = repo.get("repo_intents", {})

    if "learn" in goal and intents.get("learning", 0) >= 0.35:
        return "Learning and skill development"
    if "contribut" in goal and repo.get("contribution_score", 0) >= 0.35:
        return "Open-source contribution"
    if ("production" in goal or "use" in goal) and intents.get("production", 0) >= 0.35:
        return "Production usage or practical reference"

    candidates = {
        "Learning and exploration": intents.get("learning", 0),
        "Open-source contribution": intents.get("contribution", 0),
        "Production usage or practical reference": intents.get("production", 0),
        "Research or experimentation": intents.get("research", 0),
        "Tool usage": intents.get("tool_usage", 0),
        "Portfolio project inspiration": intents.get("portfolio", 0),
    }
    best_label, best_score = max(candidates.items(), key=lambda item: item[1])
    return best_label if best_score > 0.15 else "General exploration"


def detect_strengths(
    repo: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    score_breakdown: Optional[Dict[str, float]] = None,
) -> List[str]:
    repo = enrich_repo(repo)
    score_breakdown = score_breakdown or {}
    strengths: List[str] = []

    if profile_language_match(repo, profile):
        strengths.append("Matches the user's preferred programming language")

    if repo.get("documentation_score", 0) >= 0.70:
        strengths.append("Strong documentation signals")
    elif repo.get("documentation_score", 0) >= 0.50:
        strengths.append("Acceptable documentation signals")

    if repo.get("health_score", 0) >= 0.70:
        strengths.append("Good repository health signals")

    if repo.get("contribution_score", 0) >= 0.60:
        strengths.append("Good contribution readiness signals")

    sections = repo.get("readme_sections", {})
    if sections.get("installation"):
        strengths.append("Includes installation or setup guidance")
    if sections.get("examples") or sections.get("usage"):
        strengths.append("Includes usage examples or practical guidance")
    if sections.get("testing"):
        strengths.append("Mentions tests or quality checks")

    if score_breakdown.get("semantic", 0) >= 0.70:
        strengths.append("Strong semantic match with the search query")
    if score_breakdown.get("bm25", 0) >= 0.70:
        strengths.append("Strong keyword match with the search query")
    if score_breakdown.get("profile", 0) >= 0.50:
        strengths.append("Good match with the user's profile")

    if not strengths:
        strengths.append("Relevant based on available repository metadata and search signals")

    return strengths[:6]


def detect_weaknesses(repo: Dict[str, Any]) -> List[str]:
    repo = enrich_repo(repo)
    weaknesses: List[str] = []

    if repo.get("documentation_score", 0) < 0.40:
        weaknesses.append("Documentation may be limited")
    if repo.get("contribution_score", 0) < 0.35:
        weaknesses.append("Limited contribution readiness signals")
    if repo.get("health_score", 0) < 0.40:
        weaknesses.append("Repository health signals may be weak or incomplete")

    sections = repo.get("readme_sections", {})
    if not sections.get("installation"):
        weaknesses.append("Setup or installation instructions may be missing")
    if not sections.get("examples") and not sections.get("usage"):
        weaknesses.append("Examples or usage guidance may be limited")

    if not repo.get("license") and not sections.get("license"):
        weaknesses.append("License information is not clearly detected from the available data")

    if not weaknesses:
        weaknesses.append("No major weakness detected from the available metadata")

    return weaknesses[:5]


def why_recommended(
    repo: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    query: Optional[str] = None,
    score_breakdown: Optional[Dict[str, float]] = None,
) -> List[str]:
    repo = enrich_repo(repo)
    score_breakdown = score_breakdown or {}
    reasons: List[str] = []

    if query:
        reasons.append(f"Relevant to the search query: '{query}'")

    if score_breakdown.get("bm25", 0) >= 0.60:
        reasons.append("High BM25 lexical relevance")
    if score_breakdown.get("semantic", 0) >= 0.60:
        reasons.append("High semantic similarity with the query")
    if score_breakdown.get("profile", 0) >= 0.50:
        reasons.append("Matches the user's profile preferences")

    if profile_language_match(repo, profile):
        reasons.append("Matches the preferred programming language")

    goal = str((profile or {}).get("goal") or "").lower()
    intents = repo.get("repo_intents", {})
    if "learn" in goal and intents.get("learning", 0) >= 0.35:
        reasons.append("Contains learning-friendly signals")
    if "contribut" in goal and repo.get("contribution_score", 0) >= 0.35:
        reasons.append("Contains contribution-related signals")
    if ("production" in goal or "use" in goal) and intents.get("production", 0) >= 0.35:
        reasons.append("Contains production/practical usage signals")

    if not reasons:
        reasons.append("Recommended based on hybrid search and repository metadata")

    return reasons[:6]


def explain_repo(
    repo: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    query: Optional[str] = None,
    score_breakdown: Optional[Dict[str, float]] = None,
    include_roadmap: bool = True,
) -> Dict[str, Any]:
    repo = enrich_repo(repo)
    roadmap = generate_roadmap(repo, profile) if include_roadmap else None

    return {
        "repo_name": get_repo_name(repo),
        "repo_url": get_repo_url(repo),
        "summary": build_summary(repo),
        "best_for": detect_best_for(repo, profile),
        "difficulty": repo.get("difficulty"),
        "technologies": repo.get("tech_stack", []),
        "topics": repo.get("topics", [])[:8],
        "scores": {
            "documentation_score": repo.get("documentation_score", 0),
            "contribution_score": repo.get("contribution_score", 0),
            "health_score": repo.get("health_score", 0),
            "repo_intents": repo.get("repo_intents", {}),
            **(score_breakdown or {}),
        },
        "strengths": detect_strengths(repo, profile, score_breakdown),
        "weaknesses": detect_weaknesses(repo),
        "why_recommended": why_recommended(repo, profile, query, score_breakdown),
        "roadmap": roadmap,
    }
