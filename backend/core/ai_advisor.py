"""
AI Advisor for OpenSeek.

This advisor works after search/recommendation. It takes top results, explains them,
chooses a recommended repo, and returns an action roadmap.

It is "AI Advisor" in the product sense, but template/rule based for now:
- grounded in retrieved repos
- no hallucination
- no LLM dependency
- later upgradeable to RAG
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.core.repo_intelligence import normalize_result_item, get_repo_name
from backend.core.repo_explainer import explain_repo
from backend.core.roadmap_generator import generate_roadmap


def _advisor_score(repo: Dict[str, Any], score_breakdown: Dict[str, float], profile: Optional[Dict[str, Any]]) -> float:
    goal = str((profile or {}).get("goal") or "").lower()

    score = 0.0
    score += score_breakdown.get("final_score", score_breakdown.get("score", 0)) * 0.35
    score += score_breakdown.get("semantic", 0) * 0.15
    score += score_breakdown.get("profile", 0) * 0.10
    score += repo.get("documentation_score", 0) * 0.15
    score += repo.get("health_score", 0) * 0.15

    if "learn" in goal:
        score += repo.get("repo_intents", {}).get("learning", 0) * 0.10
        if repo.get("difficulty") == "beginner":
            score += 0.05
    elif "contribut" in goal:
        score += repo.get("contribution_score", 0) * 0.15
    elif "production" in goal or "use" in goal:
        score += repo.get("repo_intents", {}).get("production", 0) * 0.10
        score += repo.get("quality_score", 0.5) * 0.05
    else:
        score += repo.get("repo_intents", {}).get("tool_usage", 0) * 0.05

    return score


def _pick_best_by(explained_items: List[Dict[str, Any]], key: str) -> Optional[str]:
    if not explained_items:
        return None
    best = max(
        explained_items,
        key=lambda item: item["repo"].get("repo_intents", {}).get(key, 0)
        if key != "contribution"
        else item["repo"].get("contribution_score", 0),
    )
    return get_repo_name(best["repo"])


def build_summary(
    query: str,
    profile: Optional[Dict[str, Any]],
    recommended_item: Dict[str, Any],
    explained_items: List[Dict[str, Any]],
) -> str:
    recommended_repo = recommended_item["repo"]
    name = get_repo_name(recommended_repo)
    goal = (profile or {}).get("goal", "your goal")
    level = (profile or {}).get("level", (profile or {}).get("skill_level", "your level"))
    language = (profile or {}).get("language", "your preferred language")
    best_for = recommended_item["explanation"].get("best_for", "your use case")

    alternatives = [get_repo_name(item["repo"]) for item in explained_items if item is not recommended_item][:2]
    alt_text = ""
    if alternatives:
        alt_text = f" You can compare it with {', '.join(alternatives)} to understand the trade-offs."

    return (
        f"Based on the query '{query}' and the profile ({language}, {level}, {goal}), "
        f"the best starting point is {name}. It appears suitable for {best_for.lower()} "
        f"and has useful signals from metadata, README-derived features, and ranking scores."
        f"{alt_text}"
    )


def advise(
    query: str,
    profile: Dict[str, Any],
    results: List[Dict[str, Any]],
    top_k: int = 5,
) -> Dict[str, Any]:
    explained_items: List[Dict[str, Any]] = []

    for raw_item in results[:top_k]:
        repo, score_breakdown = normalize_result_item(raw_item)
        explanation = explain_repo(repo, profile=profile, query=query, score_breakdown=score_breakdown)
        advisor_score = _advisor_score(repo, score_breakdown, profile)

        explained_items.append(
            {
                "repo": repo,
                "score_breakdown": score_breakdown,
                "advisor_score": round(advisor_score, 3),
                "explanation": explanation,
            }
        )

    if not explained_items:
        return {
            "summary": "No repositories were provided to the advisor.",
            "recommended_repo": None,
            "recommended_order": [],
            "top_explanations": [],
        }

    explained_items.sort(key=lambda item: item["advisor_score"], reverse=True)
    recommended = explained_items[0]

    return {
        "summary": build_summary(query, profile, recommended, explained_items),
        "recommended_repo": get_repo_name(recommended["repo"]),
        "recommended_order": [get_repo_name(item["repo"]) for item in explained_items],
        "best_for_learning": _pick_best_by(explained_items, "learning"),
        "best_for_contribution": _pick_best_by(explained_items, "contribution"),
        "best_for_production": _pick_best_by(explained_items, "production"),
        "roadmap_for_recommended_repo": generate_roadmap(recommended["repo"], profile),
        "top_explanations": [
            {
                "repo_name": get_repo_name(item["repo"]),
                "advisor_score": item["advisor_score"],
                "score_breakdown": item["score_breakdown"],
                "explanation": item["explanation"],
            }
            for item in explained_items
        ],
    }
