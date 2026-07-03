"""
Repo Explainer for OpenSeek.

Explains one repository using metadata, README-derived features, score breakdown,
and user profile. This is the "Understand this repo" feature.
"""

from __future__ import annotations

import hashlib
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
    roadmap = generate_roadmap(repo, profile, query=query) if include_roadmap else None

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


def _format_steps_roadmap(roadmap: Dict[str, Any]) -> str:
    lines = [roadmap.get("title", "Learning Roadmap"), ""]
    for i, step in enumerate(roadmap.get("steps") or [], 1):
        if isinstance(step, dict):
            title = step.get("title") or step.get("name") or f"Step {i}"
            desc = step.get("description") or ""
            lines.append(f"{i}. {title}")
            if desc:
                lines.append(f"   {desc}")
        else:
            lines.append(f"{i}. {step}")
    return "\n".join(lines)


def _pick_variant(seed: str, options: List[str]) -> str:
    if not options:
        return ""
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def _repo_facts(repo: Dict[str, Any], explained: Dict[str, Any]) -> Dict[str, str]:
    topics = ", ".join((repo.get("topics") or [])[:5]) or "general development"
    tech = ", ".join((explained.get("technologies") or repo.get("tech_stack") or [])[:5])
    lang = repo.get("language") or "unspecified"
    stars = repo.get("stars") or repo.get("stargazers_count") or "unknown"
    return {
        "topics": topics,
        "tech": tech or lang,
        "lang": lang,
        "stars": str(stars),
        "difficulty": explained.get("difficulty") or "not specified",
        "best_for": explained.get("best_for") or "exploration",
    }


def answer_repo_question(
    repo: Dict[str, Any],
    message: str,
    profile: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Query-aware rule-based answer grounded in the selected repository."""
    history = history or []
    repo = enrich_repo(repo)
    name = get_repo_name(repo)
    q = message.lower().strip()
    explained = explain_repo(repo, profile, query=message, include_roadmap=False)
    facts = _repo_facts(repo, explained)
    seed = f"{name}|{message}|{len(history)}"

    if any(k in q for k in ("roadmap", "learning path", "step by step", "how do i learn", "study plan")):
        roadmap = generate_roadmap(repo, profile, query=message)
        intro = _pick_variant(seed, [
            f"Here is a personalized roadmap for **{name}** based on your question:",
            f"For **{name}** ({facts['lang']}, topics: {facts['topics']}), here is a practical path:",
            f"Tailored learning plan for **{name}** — grounded in its metadata and documentation signals:",
        ])
        answer = f"{intro}\n\n{_format_steps_roadmap(roadmap)}"
        return {
            "mode": "rule_based",
            "answer": answer,
            "roadmap": roadmap,
            "repo_name": name,
        }

    if any(k in q for k in ("beginner", "easy", "start", "new to", "first time", "friendly")):
        answer = _pick_variant(seed, [
            (
                f"**{name}** looks **{facts['difficulty']}** for newcomers. "
                f"It is mainly **{facts['lang']}** and covers {facts['topics']}.\n\n"
                f"{explained['summary']}\n\n"
                f"Start with the README installation section, then run the smallest example. "
                f"Best fit: {facts['best_for']}."
            ),
            (
                f"For beginners asking about **{name}**: difficulty is **{facts['difficulty']}**. "
                f"The repo has {facts['stars']} stars and focuses on {facts['tech']}.\n\n"
                f"{explained['summary']}\n\n"
                f"Tip: clone the repo, skim the folder structure, and change one small thing to build confidence."
            ),
            (
                f"Getting started with **{name}** — estimated level: **{facts['difficulty']}**. "
                f"Topics include {facts['topics']}.\n\n"
                f"{explained['summary']}\n\n"
                f"Recommended path: setup → README examples → one tiny modification."
            ),
        ])
    elif any(k in q for k in ("unique", "different", "special", "stand out", "why this", "makes this")):
        strengths = explained.get("strengths") or []
        bullets = "\n".join(f"• {s}" for s in strengths) or f"• Strong {facts['lang']} project in {facts['topics']}"
        answer = _pick_variant(seed, [
            f"What sets **{name}** apart:\n\n{bullets}\n\n{explained['summary']}",
            f"**{name}** is distinctive because:\n\n{bullets}\n\nWith {facts['stars']} stars, it is best for {facts['best_for']}.",
            f"Compared to similar repos, **{name}** highlights:\n\n{bullets}\n\n{explained['summary']}",
        ])
    elif any(k in q for k in ("learn", "study", "skill", "understand", "teach")):
        answer = _pick_variant(seed, [
            (
                f"From **{name}** you can learn **{facts['tech']}** and topics like {facts['topics']}.\n\n"
                f"{explained['summary']}\n\n"
                f"Focus area: {facts['best_for']}."
            ),
            (
                f"**{name}** is a solid study resource for {facts['lang']} / {facts['topics']}.\n\n"
                f"{explained['summary']}\n\n"
                f"Try: read core modules, trace one feature end-to-end, then rebuild a mini version."
            ),
            (
                f"Skills you can build with **{name}**: {facts['tech']}.\n\n"
                f"{explained['summary']}\n\n"
                f"Pair reading the README with exploring how {facts['lang']} is used in the codebase."
            ),
        ])
    elif any(k in q for k in ("weak", "limit", "risk", "concern", "problem")):
        weaknesses = explained.get("weaknesses") or []
        bullets = "\n".join(f"• {w}" for w in weaknesses) or "• Limited signals in the dataset — verify maintenance and docs yourself."
        answer = _pick_variant(seed, [
            f"Watch-outs for **{name}**:\n\n{bullets}",
            f"Before committing to **{name}**, consider:\n\n{bullets}\n\nStars: {facts['stars']}; difficulty: {facts['difficulty']}.",
        ])
    elif any(k in q for k in ("contribut", "open source", "pull request", "issue")):
        roadmap = generate_roadmap(repo, profile, query="contribution")
        answer = (
            f"Contribution path for **{name}**:\n\n"
            f"{_format_steps_roadmap(roadmap)}"
        )
        return {
            "mode": "rule_based",
            "answer": answer,
            "roadmap": roadmap,
            "repo_name": name,
        }
    elif history and any(k in q for k in ("more", "else", "another", "follow up", "tell me more")):
        answer = _pick_variant(seed, [
            (
                f"Building on our chat about **{name}**: {explained['summary']}\n\n"
                f"Deeper angle — explore {facts['topics']} in the source and compare with a similar {facts['lang']} repo."
            ),
            (
                f"Another take on **{name}**: strengths include "
                + (
                    "; ".join((explained.get("strengths") or [])[:3])
                    or "solid metadata match"
                )
                + ".\n\nNext: try the roadmap or ask about contribution steps."
            ),
        ])
    else:
        strengths = "\n".join(f"• {s}" for s in (explained.get("strengths") or [])[:4])
        weaknesses = "\n".join(f"• {w}" for w in (explained.get("weaknesses") or [])[:3])
        answer = _pick_variant(seed, [
            (
                f"About **{name}** ({facts['lang']}, {facts['stars']} stars) — \"{message}\"\n\n"
                f"{explained['summary']}\n\n"
                f"**Best for:** {facts['best_for']}\n"
                f"**Difficulty:** {facts['difficulty']}\n\n"
                f"**Strengths:**\n{strengths or '• Relevant based on available metadata'}\n\n"
                f"**Considerations:**\n{weaknesses or '• No major issues detected'}"
            ),
            (
                f"For **{name}**, regarding \"{message}\":\n\n"
                f"{explained['summary']}\n\n"
                f"Technologies: {facts['tech']}. Topics: {facts['topics']}.\n"
                f"Suited for {facts['best_for']} at **{facts['difficulty']}** level."
            ),
            (
                f"**{name}** in context: {explained['summary']}\n\n"
                f"Your question: \"{message}\"\n\n"
                f"Key strengths:\n{strengths or '• Good match for the selected repo'}\n\n"
                f"Ask about roadmap, beginner tips, or what makes this repo unique."
            ),
        ])

    return {
        "mode": "rule_based",
        "answer": answer,
        "repo_name": name,
        "context": explained,
    }
