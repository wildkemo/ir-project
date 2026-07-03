from __future__ import annotations

from typing import Any, Dict, Optional

from backend.core.llm_client import LLMClient
from backend.core.repo_intelligence import enrich_repo, get_repo_name, get_repo_readme_text


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
    enriched = enrich_repo(repo)
    readme = get_repo_readme_text(enriched)
    readme_preview = readme[:4000] if readme else "Not available in the dataset"
    sections = enriched.get("readme_sections") or {}
    detected_sections = ", ".join(name for name, present in sections.items() if present) or "none detected"

    return f"""
USER QUERY:
{query or "Not provided"}

USER PROFILE:
{_safe(profile)}

REPOSITORY DATA:
Name: {_safe(get_repo_name(enriched))}
URL: {_safe(enriched.get("html_url") or enriched.get("url"))}
Description: {_safe(enriched.get("description"))}
Language: {_safe(enriched.get("language"))}
Topics: {_safe(enriched.get("topics"))}
Tech stack: {_safe(enriched.get("tech_stack"))}
Stars: {_safe(enriched.get("stars") or enriched.get("stargazers_count"))}
Forks: {_safe(enriched.get("forks") or enriched.get("forks_count"))}
License: {_safe(enriched.get("license"))}
Difficulty estimate: {_safe(enriched.get("difficulty"))}
Documentation score: {_safe(enriched.get("documentation_score"))}
Health score: {_safe(enriched.get("health_score"))}
Contribution readiness: {_safe(enriched.get("contribution_score"))}
README sections detected: {detected_sections}

SCORES:
Final score: {_safe(enriched.get("score") or enriched.get("final_score"))}
Score breakdown: {_safe(enriched.get("score_breakdown"))}

README / PROCESSED CONTENT:
{readme_preview}
""".strip()


def explain_repo_with_rag(
    repo: Dict[str, Any],
    query: Optional[str] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = build_repo_context(repo, query, profile)
    repo_name = get_repo_name(repo)

    system_prompt = """
You are RepoMind AI Advisor.

Use ONLY the provided repository data for the SELECTED repository.
Do not invent missing details.
If something is missing, say "Not available in the dataset".
Tailor every answer to the specific repository named in the context.
""".strip()

    user_prompt = f"""
Explain the GitHub repository **{repo_name}** for the user.

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
        temperature=0.65,
        max_tokens=900,
    )

    return {
        "mode": "rag_ollama",
        "model": client.model,
        "answer": answer,
        "repo_name": repo_name,
    }


def generate_roadmap_with_rag(
    repo: Dict[str, Any],
    query: Optional[str] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    context = build_repo_context(repo, query, profile)
    repo_name = get_repo_name(repo)

    system_prompt = f"""
You are RepoMind AI Roadmap Advisor.

You are creating a roadmap for ONE specific repository: **{repo_name}**.
Use ONLY the provided repository data — language, topics, README/processed content, and metadata.
Do not invent setup steps that are not supported by the data.
If README/setup information is missing, say that clearly and suggest safe generic next steps.
Each roadmap must be unique to this repository (not a generic React/Python tutorial unless that is the repo).
""".strip()

    user_prompt = f"""
Create a practical learning/usage roadmap for **{repo_name}**.

User focus: {query or "General learning path tailored to this repository"}

Use this structure:
1. Roadmap Goal (specific to {repo_name})
2. Before You Start (prerequisites based on language/topics)
3. Step-by-Step Roadmap (5–8 concrete steps referencing this repo)
4. What to focus on in the README
5. Small project/task to try with this repo
6. Contribution path if the data supports it
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
        temperature=0.72,
        max_tokens=1100,
    )

    return {
        "mode": "rag_ollama",
        "model": client.model,
        "answer": answer,
        "roadmap_type": "rag",
        "repo_name": repo_name,
    }


def chat_about_repo(
    repo: Dict[str, Any],
    message: str,
    profile: Optional[Dict[str, Any]] = None,
    history: Optional[list[dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Conversational Q&A about one repository with message history."""
    repo_name = get_repo_name(repo)
    context = build_repo_context(repo, message, profile)
    history = history or []

    system_prompt = f"""
You are RepoMind AI Advisor — a helpful assistant that answers questions about ONE GitHub repository: **{repo_name}**.

Rules:
- Use ONLY the repository context below. Do not invent facts.
- If data is missing, say "Not available in the dataset".
- Answer the user's specific question directly and conversationally.
- Every reply must be grounded in **{repo_name}** (its language, topics, description, README).
- Vary your wording and structure; do not repeat the same template across messages.
- If the user asks a similar question again, give a fresh angle or deeper detail.
- Keep answers practical and focused on the selected repo.
- You may reference earlier messages in the conversation when relevant.

REPOSITORY CONTEXT:
{context}
""".strip()

    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    for item in history[-8:]:
        role = item.get("role", "user")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": str(item.get("content", ""))[:2000]})
    messages.append({"role": "user", "content": message})

    client = LLMClient()
    answer = client.generate(
        messages=messages,
        temperature=0.78,
        max_tokens=900,
    )

    return {
        "mode": "rag_ollama",
        "model": client.model,
        "answer": answer,
        "repo_name": repo_name,
    }
