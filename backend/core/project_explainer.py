"""
Project Explainer / Repository Summarizer for OpenSeek.

Goal:
- Explain a selected GitHub repository in detail without forcing the user to open GitHub.
- Uses only repository data already available in the system:
  README, stars, forks, contributors/contributors_count if available,
  technologies, topics, language, dates, scores, and metadata.

This module is template-based and grounded in the dataset.
It does NOT call an LLM and does NOT invent missing information.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


TECH_KEYWORDS = {
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
    "spring": ["spring boot", "spring"],
    "laravel": ["laravel"],
    "rails": ["ruby on rails", "rails"],
    "mongodb": ["mongodb", "mongo"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "sqlite": ["sqlite"],
    "redis": ["redis"],
    "docker": ["docker", "dockerfile"],
    "kubernetes": ["kubernetes", "k8s"],
    "graphql": ["graphql"],
    "rest api": ["rest api", "restful", "api endpoint", "api endpoints"],
    "jwt": ["jwt", "json web token"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "torch"],
    "opencv": ["opencv", "cv2"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "tailwind": ["tailwind", "tailwindcss"],
    "typescript": ["typescript", "ts "],
    "javascript": ["javascript", "js "],
    "python": ["python"],
}


SECTION_ALIASES = {
    "installation": ["installation", "install", "setup", "getting started", "quick start", "quickstart"],
    "usage": ["usage", "how to use", "running", "run", "example usage"],
    "examples": ["examples", "demo", "sample", "screenshots"],
    "configuration": ["configuration", "config", "environment variables", ".env"],
    "api": ["api", "api reference", "endpoints", "routes"],
    "contributing": ["contributing", "contribute", "pull request", "pull requests"],
    "license": ["license"],
    "testing": ["testing", "tests", "run tests", "unit tests"],
    "deployment": ["deployment", "deploy", "docker", "production"],
}


def _first(repo: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        value = repo.get(key)
        if value not in (None, "", [], {}):
            return value
    return default


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(x) for x in value)
    if isinstance(value, dict):
        return " ".join(f"{k} {v}" for k, v in value.items())
    return str(value)


def normalize_repo(repo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supports multiple repo shapes:
    - raw GitHub API-like data
    - processed.json style
    - search result item with nested "repo"
    - frontend flat repo card data
    """
    if "repo" in repo and isinstance(repo["repo"], dict):
        nested = dict(repo["repo"])
        # keep scores if provided outside
        if "score_breakdown" in repo and "score_breakdown" not in nested:
            nested["score_breakdown"] = repo["score_breakdown"]
        return normalize_repo(nested)

    normalized = dict(repo)

    normalized["name"] = _first(repo, ["name", "title", "repo_name", "full_name"], "Unknown repository")
    normalized["full_name"] = _first(repo, ["full_name", "fullname", "repo_full_name"], normalized["name"])
    normalized["url"] = _first(repo, ["html_url", "url", "github_url", "repo_url"], "")
    normalized["description"] = _first(repo, ["description", "summary"], "No description available in the dataset.")
    normalized["language"] = _first(repo, ["language", "main_language"], "Unknown")
    normalized["topics"] = _first(repo, ["topics", "tags", "topic_list"], []) or []
    normalized["readme"] = _first(repo, ["readme", "README", "readme_text", "content"], "") or ""
    normalized["stars"] = int(_first(repo, ["stars", "stargazers_count", "star_count"], 0) or 0)
    normalized["forks"] = int(_first(repo, ["forks", "forks_count", "fork_count"], 0) or 0)
    normalized["watchers"] = int(_first(repo, ["watchers", "watchers_count"], 0) or 0)
    normalized["open_issues"] = int(_first(repo, ["open_issues_count", "open_issues", "issues"], 0) or 0)
    normalized["license"] = _extract_license(_first(repo, ["license", "license_type"], None))
    normalized["created_at"] = _first(repo, ["created_at", "created"], None)
    normalized["updated_at"] = _first(repo, ["updated_at", "pushed_at", "last_update", "updated"], None)

    contributors = _first(repo, ["contributors", "contributors_list"], [])
    contributors_count = _first(repo, ["contributors_count", "contributor_count", "contributors_total"], None)
    if contributors_count is None:
        contributors_count = len(contributors) if isinstance(contributors, list) else None
    normalized["contributors"] = contributors if isinstance(contributors, list) else []
    normalized["contributors_count"] = contributors_count

    normalized["score_breakdown"] = _first(repo, ["score_breakdown", "scores"], {}) or {}

    return normalized


def _extract_license(value: Any) -> str:
    if value is None:
        return "Not available"
    if isinstance(value, dict):
        return value.get("spdx_id") or value.get("name") or "Available"
    return str(value) if str(value).strip() else "Not available"


def clean_markdown(text: str) -> str:
    text = text or ""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def readme_preview(readme: str, max_chars: int = 700) -> str:
    text = clean_markdown(readme)
    if not text:
        return "README content is not available in the dataset."
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def extract_readme_sections(readme: str) -> Dict[str, bool]:
    text = (readme or "").lower()
    sections = {}
    for section, aliases in SECTION_ALIASES.items():
        sections[section] = any(alias in text for alias in aliases)
    return sections


def extract_section_snippets(readme: str, max_chars: int = 420) -> Dict[str, str]:
    """
    Lightweight Markdown section extractor.
    It searches headings like ## Installation / # Usage and returns short snippets.
    """
    if not readme:
        return {}

    lines = readme.splitlines()
    sections: Dict[str, List[str]] = {}
    current_name: Optional[str] = None

    for line in lines:
        heading = re.match(r"^\s{0,3}#{1,4}\s+(.+?)\s*$", line)
        if heading:
            raw = heading.group(1).strip().lower()
            matched = None
            for section, aliases in SECTION_ALIASES.items():
                if any(alias in raw for alias in aliases):
                    matched = section
                    break
            current_name = matched
            if current_name:
                sections.setdefault(current_name, [])
            continue

        if current_name and len(" ".join(sections[current_name])) < max_chars:
            sections[current_name].append(line.strip())

    snippets = {}
    for section, section_lines in sections.items():
        snippet = clean_markdown(" ".join(section_lines))
        if snippet:
            snippets[section] = snippet[:max_chars].rsplit(" ", 1)[0] + ("..." if len(snippet) > max_chars else "")
    return snippets


def extract_tech_stack(repo: Dict[str, Any]) -> List[str]:
    existing = _first(repo, ["tech_stack", "technologies", "frameworks"], [])
    if isinstance(existing, list) and existing:
        return sorted(set(str(x).lower() for x in existing if x))

    text = " ".join([
        _as_text(repo.get("name")),
        _as_text(repo.get("description")),
        _as_text(repo.get("language")),
        _as_text(repo.get("topics")),
        _as_text(repo.get("readme")),
    ]).lower()

    found = set()
    for tech, aliases in TECH_KEYWORDS.items():
        if any(alias.lower() in text for alias in aliases):
            found.add(tech)

    language = (repo.get("language") or "").strip().lower()
    if language and language != "unknown":
        found.add(language)

    return sorted(found)


def _days_since(date_value: Any) -> Optional[int]:
    if not date_value:
        return None
    try:
        text = str(date_value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - dt).days)
    except Exception:
        return None


def calculate_documentation_score(repo: Dict[str, Any], sections: Dict[str, bool]) -> float:
    readme = repo.get("readme", "") or ""
    score = 0.0

    if len(readme) > 300:
        score += 0.15
    if len(readme) > 1000:
        score += 0.15

    for key, weight in [
        ("installation", 0.16),
        ("usage", 0.16),
        ("examples", 0.14),
        ("api", 0.10),
        ("configuration", 0.08),
        ("testing", 0.08),
        ("license", 0.06),
        ("contributing", 0.07),
    ]:
        if sections.get(key):
            score += weight

    return round(min(score, 1.0), 3)


def calculate_contribution_score(repo: Dict[str, Any], sections: Dict[str, bool]) -> float:
    text = " ".join([repo.get("readme", "") or "", _as_text(repo.get("topics"))]).lower()
    score = 0.0

    if sections.get("contributing"):
        score += 0.35
    if "good first issue" in text or "good-first-issue" in text:
        score += 0.20
    if "help wanted" in text or "help-wanted" in text:
        score += 0.15
    if "pull request" in text or "pull requests" in text or "pr " in text:
        score += 0.10
    if "code of conduct" in text:
        score += 0.10

    contributors_count = repo.get("contributors_count")
    if isinstance(contributors_count, int) and contributors_count >= 5:
        score += 0.10

    return round(min(score, 1.0), 3)


def calculate_popularity_score(repo: Dict[str, Any]) -> float:
    stars = repo.get("stars", 0) or 0
    forks = repo.get("forks", 0) or 0
    # simple saturating normalization
    score = min(1.0, (stars / 5000.0) * 0.7 + (forks / 1000.0) * 0.3)
    return round(score, 3)


def calculate_activity_score(repo: Dict[str, Any]) -> float:
    days = _days_since(repo.get("updated_at"))
    if days is None:
        return 0.4
    if days <= 30:
        return 1.0
    if days <= 90:
        return 0.85
    if days <= 180:
        return 0.7
    if days <= 365:
        return 0.55
    if days <= 730:
        return 0.35
    return 0.15


def calculate_health_score(repo: Dict[str, Any], doc_score: float, contribution_score: float) -> float:
    existing = repo.get("health_score")
    if isinstance(existing, (int, float)):
        return round(float(existing), 3)

    popularity = calculate_popularity_score(repo)
    activity = calculate_activity_score(repo)
    license_score = 0.1 if repo.get("license", "Not available") != "Not available" else 0.0

    health = (
        doc_score * 0.35
        + activity * 0.25
        + popularity * 0.20
        + contribution_score * 0.10
        + license_score
    )
    return round(min(health, 1.0), 3)


def infer_difficulty(repo: Dict[str, Any], sections: Dict[str, bool], tech_stack: List[str]) -> str:
    existing = repo.get("difficulty")
    if existing:
        return str(existing)

    text = " ".join([repo.get("description", ""), repo.get("readme", ""), _as_text(repo.get("topics"))]).lower()
    beginner_terms = ["beginner", "tutorial", "learn", "starter", "example", "simple", "course", "getting started"]
    advanced_terms = ["distributed", "scalable", "kubernetes", "compiler", "performance", "microservice", "architecture", "production"]

    beginner_score = sum(1 for t in beginner_terms if t in text)
    advanced_score = sum(1 for t in advanced_terms if t in text)

    if beginner_score >= 2 or (sections.get("examples") and sections.get("installation")):
        return "beginner"
    if advanced_score >= 2 or len(tech_stack) >= 6:
        return "advanced"
    return "intermediate"


def infer_repo_intents(repo: Dict[str, Any], sections: Dict[str, bool], doc_score: float, contribution_score: float) -> Dict[str, float]:
    existing = repo.get("repo_intents")
    if isinstance(existing, dict) and existing:
        return existing

    text = " ".join([repo.get("description", ""), repo.get("readme", ""), _as_text(repo.get("topics"))]).lower()

    learning = 0.0
    production = 0.0
    contribution = contribution_score

    if any(t in text for t in ["tutorial", "learn", "course", "example", "starter", "beginner"]):
        learning += 0.35
    if sections.get("installation"):
        learning += 0.15
    if sections.get("usage") or sections.get("examples"):
        learning += 0.20
    learning += doc_score * 0.30

    if any(t in text for t in ["production", "deployment", "docker", "stable", "enterprise", "scalable"]):
        production += 0.35
    if sections.get("deployment"):
        production += 0.20
    if sections.get("configuration"):
        production += 0.15
    production += calculate_activity_score(repo) * 0.15
    production += (0.15 if repo.get("license", "Not available") != "Not available" else 0.0)

    return {
        "learning": round(min(learning, 1.0), 3),
        "production": round(min(production, 1.0), 3),
        "contribution": round(min(contribution, 1.0), 3),
    }


def enrich_repo(repo_data: Dict[str, Any]) -> Dict[str, Any]:
    repo = normalize_repo(repo_data)

    repo["readme_sections"] = _first(repo, ["readme_sections"], None) or extract_readme_sections(repo.get("readme", ""))
    repo["readme_section_snippets"] = _first(repo, ["readme_section_snippets"], None) or extract_section_snippets(repo.get("readme", ""))
    repo["tech_stack"] = extract_tech_stack(repo)

    repo["documentation_score"] = float(_first(repo, ["documentation_score"], None) or calculate_documentation_score(repo, repo["readme_sections"]))
    repo["contribution_score"] = float(_first(repo, ["contribution_score"], None) or calculate_contribution_score(repo, repo["readme_sections"]))
    repo["health_score"] = float(_first(repo, ["health_score"], None) or calculate_health_score(repo, repo["documentation_score"], repo["contribution_score"]))
    repo["popularity_score"] = float(_first(repo, ["popularity_score"], None) or calculate_popularity_score(repo))
    repo["activity_score"] = float(_first(repo, ["activity_score"], None) or calculate_activity_score(repo))
    repo["difficulty"] = infer_difficulty(repo, repo["readme_sections"], repo["tech_stack"])
    repo["repo_intents"] = infer_repo_intents(repo, repo["readme_sections"], repo["documentation_score"], repo["contribution_score"])
    repo["readme_preview"] = readme_preview(repo.get("readme", ""))

    return repo


def _score_label(score: float) -> str:
    if score >= 0.75:
        return "Strong"
    if score >= 0.5:
        return "Medium"
    if score >= 0.25:
        return "Limited"
    return "Weak"


def build_project_overview(repo: Dict[str, Any]) -> str:
    name = repo.get("full_name") or repo.get("name")
    description = repo.get("description", "No description available")
    language = repo.get("language", "Unknown")
    topics = repo.get("topics", []) or []
    topic_text = ", ".join(topics[:5]) if topics else "general software development"
    tech_text = ", ".join(repo.get("tech_stack", [])[:6]) or language

    return (
        f"{name} is a {language}-based GitHub repository related to {topic_text}. "
        f"Based on the available metadata and README, it appears to focus on: {description}. "
        f"Detected technologies and signals include: {tech_text}."
    )


def build_strengths(repo: Dict[str, Any]) -> List[str]:
    strengths = []

    if repo["documentation_score"] >= 0.7:
        strengths.append("Strong README/documentation signals.")
    if repo["readme_sections"].get("installation"):
        strengths.append("Includes installation or setup guidance.")
    if repo["readme_sections"].get("usage"):
        strengths.append("Includes usage instructions.")
    if repo["readme_sections"].get("examples"):
        strengths.append("Includes examples, demos, or sample usage.")
    if repo["contribution_score"] >= 0.6:
        strengths.append("Has useful contribution-readiness signals.")
    if repo["health_score"] >= 0.7:
        strengths.append("Good overall repository health based on activity, docs, and popularity signals.")
    if repo["stars"] >= 500:
        strengths.append("Has strong popularity signals from GitHub stars.")
    if repo["forks"] >= 100:
        strengths.append("Has meaningful fork activity, suggesting developer interest or reuse.")
    if repo.get("license", "Not available") != "Not available":
        strengths.append("License information is available.")

    if not strengths:
        strengths.append("Relevant repository metadata is available, but strong quality signals are limited.")

    return strengths[:7]


def build_limitations(repo: Dict[str, Any]) -> List[str]:
    limitations = []

    if not repo.get("readme"):
        limitations.append("README content is missing from the dataset.")
    if repo["documentation_score"] < 0.4:
        limitations.append("Documentation signals appear limited.")
    if not repo["readme_sections"].get("installation"):
        limitations.append("Installation/setup instructions were not clearly detected.")
    if not repo["readme_sections"].get("usage"):
        limitations.append("Usage instructions were not clearly detected.")
    if not repo["readme_sections"].get("examples"):
        limitations.append("Examples or demos were not clearly detected.")
    if repo["contribution_score"] < 0.4:
        limitations.append("Contribution-readiness signals are limited.")
    if repo.get("license", "Not available") == "Not available":
        limitations.append("License information is not available in the dataset.")
    if repo.get("contributors_count") is None:
        limitations.append("Contributor count is not available in the dataset.")

    if not limitations:
        limitations.append("No major limitations detected from the available metadata.")

    return limitations[:7]


def detect_best_for(repo: Dict[str, Any]) -> str:
    intents = repo["repo_intents"]
    difficulty = repo["difficulty"]

    if intents.get("learning", 0) >= 0.65:
        return f"Learning and exploration ({difficulty} level)"
    if intents.get("production", 0) >= 0.65:
        return "Production usage or production reference"
    if intents.get("contribution", 0) >= 0.60:
        return "Open-source contribution"
    if repo["documentation_score"] >= 0.7:
        return "Understanding and using a well-documented project"
    return "General repository discovery"


def build_how_to_use(repo: Dict[str, Any]) -> List[str]:
    sections = repo["readme_sections"]
    steps = []

    if sections.get("installation"):
        steps.append("Start with the Installation/Setup section in the README.")
    else:
        steps.append("Start by reading the README overview and identify setup requirements.")

    if sections.get("configuration"):
        steps.append("Check configuration or environment variable instructions before running it.")

    if sections.get("usage"):
        steps.append("Follow the Usage section to run the main workflow.")
    elif sections.get("examples"):
        steps.append("Run the provided examples or demos.")
    else:
        steps.append("Look for commands, examples, or entry points inside the README/repository.")

    if sections.get("testing"):
        steps.append("Run the available tests to verify the project works correctly.")

    if sections.get("api"):
        steps.append("Review the API/endpoints section to understand how to interact with the project.")

    steps.append("Use the detected technologies and topics to understand the main architecture.")
    return steps[:6]


def build_contribution_guidance(repo: Dict[str, Any]) -> List[str]:
    steps = []
    if repo["readme_sections"].get("contributing"):
        steps.append("Read the Contributing section or CONTRIBUTING guide first.")
    else:
        steps.append("Check GitHub issues and repository guidelines before contributing.")

    if repo["contribution_score"] >= 0.6:
        steps.append("Look for beginner-friendly issues such as good-first-issue or help-wanted.")
    else:
        steps.append("Start with documentation improvements or a small bug fix because contribution signals are limited.")

    steps.append("Set up the project locally and run examples/tests before opening a pull request.")
    steps.append("Keep the first contribution small and focused.")
    return steps


def explain_project(repo_data: Dict[str, Any], profile: Optional[Dict[str, Any]] = None, query: Optional[str] = None) -> Dict[str, Any]:
    repo = enrich_repo(repo_data)

    profile = profile or {}
    query = query or ""

    score_breakdown = repo.get("score_breakdown", {}) or {}

    metrics = {
        "stars": repo["stars"],
        "forks": repo["forks"],
        "contributors_count": repo["contributors_count"] if repo["contributors_count"] is not None else "Not available",
        "open_issues": repo["open_issues"],
        "watchers": repo["watchers"],
        "license": repo["license"],
        "last_updated": repo["updated_at"] or "Not available",
        "documentation_score": repo["documentation_score"],
        "contribution_score": repo["contribution_score"],
        "health_score": repo["health_score"],
        "popularity_score": repo["popularity_score"],
        "activity_score": repo["activity_score"],
    }

    readme_analysis = {
        "preview": repo["readme_preview"],
        "detected_sections": repo["readme_sections"],
        "section_snippets": repo["readme_section_snippets"],
    }

    explanation = {
        "repo_identity": {
            "name": repo["name"],
            "full_name": repo["full_name"],
            "url": repo["url"],
            "description": repo["description"],
            "language": repo["language"],
            "topics": repo["topics"],
            "technologies": repo["tech_stack"],
        },
        "project_summary": build_project_overview(repo),
        "best_for": detect_best_for(repo),
        "difficulty": repo["difficulty"],
        "metrics": metrics,
        "readme_analysis": readme_analysis,
        "scores_interpretation": {
            "documentation": _score_label(repo["documentation_score"]),
            "contribution": _score_label(repo["contribution_score"]),
            "health": _score_label(repo["health_score"]),
            "activity": _score_label(repo["activity_score"]),
            "popularity": _score_label(repo["popularity_score"]),
        },
        "strengths": build_strengths(repo),
        "limitations": build_limitations(repo),
        "how_to_use_it": build_how_to_use(repo),
        "contribution_guidance": build_contribution_guidance(repo),
        "why_it_matches": build_match_reasons(repo, profile=profile, query=query, score_breakdown=score_breakdown),
        "raw_scores": score_breakdown,
    }

    return explanation


def build_match_reasons(repo: Dict[str, Any], profile: Dict[str, Any], query: str, score_breakdown: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []

    if query:
        reasons.append(f"It was explained in the context of the user query: '{query}'.")

    preferred_language = str(profile.get("language", "")).lower()
    if preferred_language and preferred_language == str(repo.get("language", "")).lower():
        reasons.append("It matches the user's preferred programming language.")

    goal = str(profile.get("goal", "")).lower()
    if goal == "learning" and repo["repo_intents"].get("learning", 0) >= 0.5:
        reasons.append("It has learning-friendly signals from README/content.")
    elif goal == "contribution" and repo["contribution_score"] >= 0.5:
        reasons.append("It has contribution-readiness signals.")
    elif goal == "production" and repo["repo_intents"].get("production", 0) >= 0.5:
        reasons.append("It has production or usage-readiness signals.")

    bm25 = score_breakdown.get("bm25") or score_breakdown.get("bm25_score")
    semantic = score_breakdown.get("semantic") or score_breakdown.get("semantic_score")
    profile_score = score_breakdown.get("profile") or score_breakdown.get("profile_score")

    if isinstance(bm25, (int, float)) and bm25 >= 0.6:
        reasons.append("It has strong lexical relevance to the search query.")
    if isinstance(semantic, (int, float)) and semantic >= 0.6:
        reasons.append("It has strong semantic similarity with the query meaning.")
    if isinstance(profile_score, (int, float)) and profile_score >= 0.5:
        reasons.append("It aligns with the user's profile preferences.")

    if repo["documentation_score"] >= 0.7:
        reasons.append("It has strong documentation signals, making it easier to understand without opening GitHub.")

    if not reasons:
        reasons.append("It is explained based on available repository metadata, README, and quality signals.")

    return reasons[:6]
