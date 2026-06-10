"""
Repo Intelligence Utilities for OpenSeek AI Advisor.

This module enriches a repository object with advisor-friendly signals.
It is intentionally template/rule based so it can work before adding an LLM/RAG layer.

Works with both raw data.json style repos:
{
  "url", "title", "description", "stars", "forks", "issues",
  "language", "languages", "topics", "readme"
}

and processed/search-result style repos:
{
  "name", "full_name", "html_url", "score_breakdown", ...
}
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple


TECH_KEYWORDS: Dict[str, List[str]] = {
    "react": ["react", "reactjs", "react.js"],
    "nextjs": ["nextjs", "next.js"],
    "vue": ["vue", "vuejs", "vue.js"],
    "angular": ["angular"],
    "nodejs": ["nodejs", "node.js", "node "],
    "express": ["express", "expressjs", "express.js"],
    "nestjs": ["nestjs", "nest.js"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "spring": ["spring boot", "spring-framework", "spring"],
    "laravel": ["laravel"],
    "docker": ["docker", "dockerfile"],
    "kubernetes": ["kubernetes", "k8s"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "graphql": ["graphql"],
    "rest-api": ["rest api", "restful", "api server"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "opencv": ["opencv", "cv2"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "tailwind": ["tailwind"],
    "typescript": ["typescript", "ts"],
    "javascript": ["javascript", "js"],
    "python": ["python"],
    "java": ["java"],
    "go": ["golang", "go"],
    "rust": ["rust"],
}


README_SECTION_KEYWORDS: Dict[str, List[str]] = {
    "installation": ["installation", "install", "setup", "getting started", "quick start", "quickstart"],
    "usage": ["usage", "how to use", "running", "run ", "commands", "configuration"],
    "examples": ["example", "examples", "demo", "sample", "tutorial"],
    "contributing": ["contributing", "contribute", "pull request", "pr ", "good first issue", "help wanted"],
    "license": ["license", "mit license", "apache license", "gpl"],
    "api": ["api", "endpoint", "reference", "swagger", "openapi"],
    "testing": ["test", "testing", "pytest", "jest", "unittest", "coverage"],
    "deployment": ["deploy", "deployment", "docker", "kubernetes", "production"],
    "security": ["security", "authentication", "authorization", "jwt", "oauth"],
}

LEARNING_KEYWORDS = [
    "learn", "learning", "tutorial", "course", "beginner", "starter", "example",
    "examples", "demo", "step by step", "guide", "getting started", "quickstart",
    "educational", "workshop", "awesome"
]
CONTRIBUTION_KEYWORDS = [
    "contributing", "contribute", "pull request", "good first issue", "help wanted",
    "issue", "maintainer", "community", "code of conduct", "contributors"
]
PRODUCTION_KEYWORDS = [
    "production", "deployment", "deploy", "docker", "kubernetes", "scalable",
    "authentication", "authorization", "monitoring", "logging", "security",
    "stable", "enterprise", "performance", "database"
]
RESEARCH_KEYWORDS = [
    "paper", "research", "benchmark", "dataset", "experiment", "model", "neural",
    "machine learning", "deep learning", "evaluation", "state of the art"
]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(normalize_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(normalize_text(v) for v in value.values())
    return str(value)


def get_repo_name(repo: Dict[str, Any]) -> str:
    return (
        repo.get("name")
        or repo.get("title")
        or repo.get("full_name")
        or repo.get("repo_name")
        or repo.get("url", "Unknown repository").rstrip("/").split("/")[-1]
    )


def get_repo_url(repo: Dict[str, Any]) -> Optional[str]:
    return repo.get("html_url") or repo.get("url") or repo.get("repo_url")


def get_combined_text(repo: Dict[str, Any]) -> str:
    parts = [
        repo.get("title"),
        repo.get("name"),
        repo.get("full_name"),
        repo.get("description"),
        " ".join(repo.get("topics", []) or []),
        " ".join((repo.get("languages") or {}).keys()) if isinstance(repo.get("languages"), dict) else "",
        repo.get("language"),
        repo.get("readme"),
        repo.get("README"),
        repo.get("embedding_text"),
    ]
    return normalize_text(parts).lower()


def extract_tech_stack(repo: Dict[str, Any]) -> List[str]:
    existing = repo.get("tech_stack")
    if isinstance(existing, list) and existing:
        return sorted(set(str(x).lower() for x in existing))

    text = get_combined_text(repo)
    languages = repo.get("languages") or {}
    found = set()

    if isinstance(languages, dict):
        for lang in languages.keys():
            if lang:
                found.add(str(lang).lower())

    if repo.get("language"):
        found.add(str(repo["language"]).lower())

    for tech, aliases in TECH_KEYWORDS.items():
        for alias in aliases:
            if re.search(r"(?<![a-z0-9])" + re.escape(alias.lower()) + r"(?![a-z0-9])", text):
                found.add(tech)
                break

    return sorted(found)


def extract_readme_sections(repo: Dict[str, Any]) -> Dict[str, bool]:
    existing = repo.get("readme_sections")
    if isinstance(existing, dict) and existing:
        return {str(k): bool(v) for k, v in existing.items()}

    readme = normalize_text(repo.get("readme") or repo.get("README") or repo.get("description")).lower()
    sections = {}
    for section, keywords in README_SECTION_KEYWORDS.items():
        sections[section] = any(k.lower() in readme for k in keywords)
    return sections


def keyword_score(text: str, keywords: Iterable[str]) -> float:
    text = text.lower()
    if not text:
        return 0.0
    hits = sum(1 for k in keywords if k.lower() in text)
    return clamp(hits / max(3, min(8, len(list(keywords)))))


def compute_documentation_score(repo: Dict[str, Any], sections: Optional[Dict[str, bool]] = None) -> float:
    if repo.get("documentation_score") is not None:
        return clamp(float(repo["documentation_score"]))

    sections = sections or extract_readme_sections(repo)
    readme_len = len(normalize_text(repo.get("readme") or repo.get("README")))
    score = 0.0

    if readme_len > 300:
        score += 0.15
    if readme_len > 1000:
        score += 0.15
    if sections.get("installation"):
        score += 0.18
    if sections.get("usage"):
        score += 0.18
    if sections.get("examples"):
        score += 0.15
    if sections.get("api"):
        score += 0.10
    if sections.get("testing"):
        score += 0.08
    if sections.get("license"):
        score += 0.06

    return clamp(score)


def compute_contribution_score(repo: Dict[str, Any], sections: Optional[Dict[str, bool]] = None) -> float:
    if repo.get("contribution_score") is not None:
        return clamp(float(repo["contribution_score"]))

    sections = sections or extract_readme_sections(repo)
    text = get_combined_text(repo)
    score = 0.0

    if sections.get("contributing"):
        score += 0.35
    score += keyword_score(text, CONTRIBUTION_KEYWORDS) * 0.45

    issues = repo.get("issues") or repo.get("open_issues_count") or 0
    try:
        issues = float(issues)
        if issues > 0:
            score += 0.10
        if issues >= 10:
            score += 0.10
    except Exception:
        pass

    return clamp(score)


def compute_health_score(repo: Dict[str, Any], documentation_score: float, contribution_score: float) -> float:
    if repo.get("health_score") is not None:
        return clamp(float(repo["health_score"]))

    stars = repo.get("stars") or repo.get("stargazers_count") or 0
    forks = repo.get("forks") or repo.get("forks_count") or 0
    activity = repo.get("activity_score")
    quality = repo.get("quality_score")

    try:
        stars_score = clamp(math.log1p(float(stars)) / math.log1p(50000))
    except Exception:
        stars_score = 0.0
    try:
        forks_score = clamp(math.log1p(float(forks)) / math.log1p(10000))
    except Exception:
        forks_score = 0.0

    if activity is None:
        activity_score = 0.5
        updated_at = repo.get("updated_at") or repo.get("pushed_at")
        if updated_at:
            try:
                if updated_at.endswith("Z"):
                    updated_at = updated_at.replace("Z", "+00:00")
                dt = datetime.fromisoformat(updated_at)
                days = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days
                if days <= 90:
                    activity_score = 1.0
                elif days <= 365:
                    activity_score = 0.75
                elif days <= 730:
                    activity_score = 0.45
                else:
                    activity_score = 0.20
            except Exception:
                activity_score = 0.5
    else:
        activity_score = clamp(float(activity))

    quality_score = clamp(float(quality)) if quality is not None else 0.5

    return clamp(
        documentation_score * 0.25
        + contribution_score * 0.10
        + stars_score * 0.20
        + forks_score * 0.10
        + activity_score * 0.20
        + quality_score * 0.15
    )


def detect_difficulty(repo: Dict[str, Any]) -> str:
    existing = repo.get("difficulty")
    if existing:
        return str(existing).lower()

    text = get_combined_text(repo)
    beginner = keyword_score(text, LEARNING_KEYWORDS)
    advanced_terms = [
        "distributed", "scalable", "compiler", "kernel", "high performance",
        "kubernetes", "microservices", "architecture", "production", "benchmark",
        "optimization", "neural", "deep learning"
    ]
    advanced = keyword_score(text, advanced_terms)

    sections = extract_readme_sections(repo)
    if sections.get("examples") or sections.get("installation"):
        beginner += 0.15

    tech_count = len(extract_tech_stack(repo))
    if tech_count >= 6:
        advanced += 0.15

    if beginner >= 0.45 and advanced < 0.45:
        return "beginner"
    if advanced >= 0.50:
        return "advanced"
    return "intermediate"


def compute_repo_intents(repo: Dict[str, Any], sections: Optional[Dict[str, bool]] = None) -> Dict[str, float]:
    existing = repo.get("repo_intents")
    if isinstance(existing, dict) and existing:
        return {str(k): clamp(float(v)) for k, v in existing.items() if isinstance(v, (int, float))}

    sections = sections or extract_readme_sections(repo)
    text = get_combined_text(repo)

    learning = keyword_score(text, LEARNING_KEYWORDS)
    contribution = keyword_score(text, CONTRIBUTION_KEYWORDS)
    production = keyword_score(text, PRODUCTION_KEYWORDS)
    research = keyword_score(text, RESEARCH_KEYWORDS)

    if sections.get("installation"):
        learning += 0.10
        production += 0.05
    if sections.get("usage") or sections.get("examples"):
        learning += 0.15
    if sections.get("contributing"):
        contribution += 0.25
    if sections.get("deployment") or sections.get("testing") or sections.get("security"):
        production += 0.15
    if sections.get("api"):
        production += 0.05

    return {
        "learning": clamp(learning),
        "contribution": clamp(contribution),
        "production": clamp(production),
        "research": clamp(research),
        "tool_usage": clamp(keyword_score(text, ["cli", "tool", "library", "framework", "plugin", "dashboard", "extension"])),
        "portfolio": clamp(keyword_score(text, ["portfolio", "project", "starter", "clone", "template", "demo"])),
    }


def profile_language_match(repo: Dict[str, Any], profile: Optional[Dict[str, Any]]) -> bool:
    if not profile:
        return False
    preferred = str(profile.get("language") or profile.get("preferred_language") or "").strip().lower()
    if not preferred:
        return False
    repo_lang = str(repo.get("language") or "").strip().lower()
    tech_stack = [str(x).lower() for x in extract_tech_stack(repo)]
    return preferred == repo_lang or preferred in tech_stack


def enrich_repo(repo: Dict[str, Any]) -> Dict[str, Any]:
    """Return a shallow copy of repo with advisor features filled in."""
    enriched = dict(repo)

    enriched.setdefault("name", get_repo_name(enriched))
    if get_repo_url(enriched):
        enriched.setdefault("url", get_repo_url(enriched))

    sections = extract_readme_sections(enriched)
    tech_stack = extract_tech_stack(enriched)
    documentation_score = compute_documentation_score(enriched, sections)
    contribution_score = compute_contribution_score(enriched, sections)
    health_score = compute_health_score(enriched, documentation_score, contribution_score)
    difficulty = detect_difficulty(enriched)
    intents = compute_repo_intents(enriched, sections)

    enriched["readme_sections"] = sections
    enriched["tech_stack"] = tech_stack
    enriched["documentation_score"] = round(documentation_score, 3)
    enriched["contribution_score"] = round(contribution_score, 3)
    enriched["health_score"] = round(health_score, 3)
    enriched["difficulty"] = difficulty
    enriched["repo_intents"] = intents

    return enriched


def normalize_result_item(item: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """
    Search results can be either:
    1) {"repo": {...}, "score_breakdown": {...}}
    2) flat repo fields with "score_breakdown"
    3) flat repo fields with score keys.
    """
    if "repo" in item and isinstance(item["repo"], dict):
        repo = item["repo"]
        score_breakdown = item.get("score_breakdown") or repo.get("score_breakdown") or {}
    else:
        repo = item
        score_breakdown = item.get("score_breakdown") or {}

    # Normalize common score key aliases
    aliases = {
        "bm25": ["bm25", "bm25_score", "lexical_score", "query_relevance"],
        "semantic": ["semantic", "semantic_score", "semantic_similarity"],
        "profile": ["profile", "profile_score", "profile_match"],
        "final_score": ["final_score", "score", "combined_score"],
    }
    normalized = {}
    for out_key, possible in aliases.items():
        for key in possible:
            if key in score_breakdown:
                normalized[out_key] = float(score_breakdown[key])
                break
            if key in item and isinstance(item[key], (int, float)):
                normalized[out_key] = float(item[key])
                break
            if key in repo and isinstance(repo[key], (int, float)):
                normalized[out_key] = float(repo[key])
                break

    return enrich_repo(repo), normalized
