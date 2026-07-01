from __future__ import annotations

from typing import Any, Dict, Optional

from backend.core.llm_client import LLMClient


def _safe(value: Any) -> str:
    if value is None:
        return "Not available"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "Not available"
    if isinstance(value, dict):
        return ", ".join(f"{key}: {val}" for key, val in value.items()) or "Not available"
    return str(value)


def build_repo_context(
    repo: Dict[str, Any],
    query: Optional[str] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> str:
    return f"""
USER QUERY:
{query or "Not provided"}

USER PROFILE:
{_safe(profile)}

REPOSITORY DATA:
Name: {_safe(repo.get("full_name") or repo.get("name"))}
URL: {_safe(repo.get("html_url") or repo.get("url"))}
Description: {_safe(repo.get("description"))}
Language: {_safe(repo.get("language"))}
Topics: {_safe(repo.get("topics"))}
Stars: {_safe(repo.get("stars") or repo.get("stargazers_count"))}
Forks: {_safe(repo.get("forks") or repo.get("forks_count"))}
Contributors: {_safe(repo.get("contributors_count") or repo.get("contributors"))}
License: {_safe(repo.get("license"))}
Updated at: {_safe(repo.get("updated_at") or repo.get("pushed_at"))}

SCORES:
Final score: {_safe(repo.get("score") or repo.get("final_score"))}
Score breakdown: {_safe(repo.get("score_breakdown"))}

README:
{_safe(repo.get("readme") or repo.get("README") or repo.get("readme_text"))}
""".strip()


def explain_repo_with_rag(
    repo: Dict[str, Any],
    query: Optional[str] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = build_repo_context(repo, query, profile)

    system_prompt = """
You are OpenSeek AI Advisor.

Use ONLY the provided repository data.
Do not invent missing details.
If something is missing, say "Not available in the dataset".
Explain clearly and practically.
""".strip()

    user_prompt = f"""
Explain this GitHub repository for the user.

Use this structure:
1. Short Summary
2. What this repository is useful for
3. Main technologies
4. Why it matches the user query/profile
5. Strengths
6. Limitations or missing data
7. How to start with it
8. Final recommendation

Context:
{context}
""".strip()

    client = LLMClient()
    answer = client.generate(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    )

    return {
        "mode": "rag_ollama",
        "model": client.model,
        "answer": answer,
    }


def generate_roadmap_with_rag(
    repo: Dict[str, Any],
    query: Optional[str] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = build_repo_context(repo, query, profile)

    system_prompt = """
You are OpenSeek AI Roadmap Advisor.

Use ONLY the provided repository data.
Do not invent setup steps if they are not available.
If README/setup information is missing, say that clearly.
""".strip()

    user_prompt = f"""
Create a practical learning/usage roadmap for this repository.

Use this structure:
1. Roadmap Goal
2. Before You Start
3. Step-by-Step Roadmap
4. What to focus on in the README
5. Small project/task to try
6. Contribution path if possible
7. Missing data or risks
8. Next step

Context:
{context}
""".strip()

    client = LLMClient()
    answer = client.generate(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=900,
    )

    return {
        "mode": "rag_ollama",
        "model": client.model,
        "answer": answer,
    }