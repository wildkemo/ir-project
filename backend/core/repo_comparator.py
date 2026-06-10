"""
Repo Comparator for OpenSeek.

Compares two repositories side-by-side and recommends a better choice
for the current user's goal.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.core.repo_intelligence import enrich_repo, get_repo_name, profile_language_match
from backend.core.repo_explainer import detect_best_for, explain_repo


def _score_for_goal(repo: Dict[str, Any], profile: Optional[Dict[str, Any]]) -> float:
    repo = enrich_repo(repo)
    goal = str((profile or {}).get("goal") or "").lower()

    score = 0.0
    score += repo.get("documentation_score", 0) * 0.25
    score += repo.get("health_score", 0) * 0.25

    if profile_language_match(repo, profile):
        score += 0.15

    if "learn" in goal:
        score += repo.get("repo_intents", {}).get("learning", 0) * 0.25
        if repo.get("difficulty") == "beginner":
            score += 0.10
    elif "contribut" in goal:
        score += repo.get("contribution_score", 0) * 0.35
        score += repo.get("activity_score", 0.5) * 0.10
    elif "production" in goal or "use" in goal:
        score += repo.get("repo_intents", {}).get("production", 0) * 0.20
        score += repo.get("quality_score", 0.5) * 0.15
        score += repo.get("activity_score", 0.5) * 0.10
    else:
        score += repo.get("popularity_score", 0.5) * 0.10
        score += repo.get("quality_score", 0.5) * 0.10

    return score


def _format_score(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 3)
    return value


def compare_repos(
    repo_a: Dict[str, Any],
    repo_b: Dict[str, Any],
    profile: Optional[Dict[str, Any]] = None,
    query: Optional[str] = None,
) -> Dict[str, Any]:
    repo_a = enrich_repo(repo_a)
    repo_b = enrich_repo(repo_b)

    rows = [
        ("Language", repo_a.get("language", "Unknown"), repo_b.get("language", "Unknown")),
        ("Difficulty", repo_a.get("difficulty", "Unknown"), repo_b.get("difficulty", "Unknown")),
        ("Best For", detect_best_for(repo_a, profile), detect_best_for(repo_b, profile)),
        ("Tech Stack", ", ".join(repo_a.get("tech_stack", [])[:6]), ", ".join(repo_b.get("tech_stack", [])[:6])),
        ("Documentation Score", repo_a.get("documentation_score", 0), repo_b.get("documentation_score", 0)),
        ("Contribution Score", repo_a.get("contribution_score", 0), repo_b.get("contribution_score", 0)),
        ("Health Score", repo_a.get("health_score", 0), repo_b.get("health_score", 0)),
        ("Stars", repo_a.get("stars", repo_a.get("stargazers_count", 0)), repo_b.get("stars", repo_b.get("stargazers_count", 0))),
        ("Forks", repo_a.get("forks", repo_a.get("forks_count", 0)), repo_b.get("forks", repo_b.get("forks_count", 0))),
    ]

    comparison_table = [
        {"feature": feature, "repo_a": _format_score(a), "repo_b": _format_score(b)}
        for feature, a, b in rows
    ]

    score_a = _score_for_goal(repo_a, profile)
    score_b = _score_for_goal(repo_b, profile)
    winner = repo_a if score_a >= score_b else repo_b
    loser = repo_b if winner is repo_a else repo_a

    winner_name = get_repo_name(winner)
    loser_name = get_repo_name(loser)
    goal = (profile or {}).get("goal", "the current goal")

    recommendation = (
        f"For {goal}, {winner_name} looks like the stronger choice based on the available "
        f"documentation, health, profile, and goal-related signals. Compare it with {loser_name} "
        f"if you need a different trade-off."
    )

    return {
        "repo_a": get_repo_name(repo_a),
        "repo_b": get_repo_name(repo_b),
        "comparison_table": comparison_table,
        "repo_a_goal_score": round(score_a, 3),
        "repo_b_goal_score": round(score_b, 3),
        "winner": winner_name,
        "recommendation": recommendation,
        "repo_a_explainer": explain_repo(repo_a, profile, query, include_roadmap=False),
        "repo_b_explainer": explain_repo(repo_b, profile, query, include_roadmap=False),
    }
