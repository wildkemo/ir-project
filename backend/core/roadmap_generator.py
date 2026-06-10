"""
Personalized Roadmap Generator for OpenSeek.

It generates actionable next steps after the user chooses a repo.
No LLM required. Safe for demo and grounded in repo metadata.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.core.repo_intelligence import enrich_repo, get_repo_name


def _goal(profile: Optional[Dict[str, Any]]) -> str:
    return str((profile or {}).get("goal") or (profile or {}).get("user_goal") or "").lower().strip()


def _level(profile: Optional[Dict[str, Any]]) -> str:
    return str((profile or {}).get("level") or (profile or {}).get("skill_level") or "").lower().strip()


def _common_start(repo: Dict[str, Any]) -> List[str]:
    repo = enrich_repo(repo)
    sections = repo.get("readme_sections", {})
    steps = [f"Start by reading the README to understand what {get_repo_name(repo)} does."]

    if sections.get("installation"):
        steps.append("Follow the installation/setup section and run the project locally.")
    else:
        steps.append("Look for setup requirements in the README, package files, or documentation.")

    if sections.get("usage") or sections.get("examples"):
        steps.append("Run the provided usage example, demo, or sample command.")
    else:
        steps.append("Identify the main entry point and try to run a minimal example.")

    tech_stack = repo.get("tech_stack", [])
    if tech_stack:
        steps.append(f"Review the main technologies used: {', '.join(tech_stack[:5])}.")

    return steps


def generate_learning_roadmap(repo: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    repo = enrich_repo(repo)
    steps = _common_start(repo)
    level = _level(profile)

    steps.append("Study the main folders and understand how the project is structured.")
    if level == "beginner":
        steps.append("Modify a very small part, such as a message, route, component, or configuration.")
        steps.append("Write notes about unfamiliar dependencies, files, and concepts.")
    else:
        steps.append("Implement a small feature or improvement to test your understanding.")

    steps.append("Compare this repository with one more advanced related repo as a next learning step.")

    return {
        "roadmap_type": "learning",
        "title": f"Learning roadmap for {get_repo_name(repo)}",
        "steps": steps[:7],
    }


def generate_contribution_roadmap(repo: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    repo = enrich_repo(repo)
    sections = repo.get("readme_sections", {})
    steps = _common_start(repo)

    if sections.get("contributing"):
        steps.append("Read the contributing guide carefully before making changes.")
    else:
        steps.append("Check the GitHub issues, pull requests, and repository guidelines manually.")

    if repo.get("contribution_score", 0) >= 0.5:
        steps.append("Look for good-first-issue, help-wanted, documentation, or small bug-fix tasks.")
    else:
        steps.append("Start with a safe contribution such as documentation improvement or typo fixes.")

    if sections.get("testing"):
        steps.append("Run the project tests before submitting any changes.")
    else:
        steps.append("Run the project locally and manually verify your change.")

    steps.append("Open a small pull request and explain your change clearly.")

    return {
        "roadmap_type": "contribution",
        "title": f"Contribution roadmap for {get_repo_name(repo)}",
        "steps": steps[:8],
    }


def generate_production_roadmap(repo: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    repo = enrich_repo(repo)
    sections = repo.get("readme_sections", {})
    steps = _common_start(repo)

    steps.append("Check license, maintenance activity, stars/forks, and repository health before adoption.")

    if sections.get("testing"):
        steps.append("Review the testing instructions and run tests locally.")
    else:
        steps.append("Check whether the project has tests or quality checks before using it seriously.")

    if sections.get("deployment"):
        steps.append("Review deployment or Docker/Kubernetes instructions.")
    else:
        steps.append("Identify how configuration, environment variables, and deployment should be handled.")

    steps.append("Build a small prototype before integrating it into a real project.")
    steps.append("Compare it with similar repositories before final adoption.")

    return {
        "roadmap_type": "production",
        "title": f"Production usage roadmap for {get_repo_name(repo)}",
        "steps": steps[:8],
    }


def generate_portfolio_roadmap(repo: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    repo = enrich_repo(repo)
    steps = _common_start(repo)

    steps.append("Fork or clone the repository and make it run locally.")
    steps.append("Customize one visible feature so the project becomes unique.")
    steps.append("Add documentation explaining what you changed and why.")
    steps.append("Deploy or record a demo if the project supports it.")
    steps.append("Write a short portfolio case study about the technologies and improvements.")

    return {
        "roadmap_type": "portfolio",
        "title": f"Portfolio roadmap for {get_repo_name(repo)}",
        "steps": steps[:8],
    }


def generate_general_roadmap(repo: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    repo = enrich_repo(repo)
    steps = _common_start(repo)
    steps.append("Explore the source code and identify the main modules.")
    steps.append("Try a small local change and verify the output.")
    steps.append("Use the repo explanation and comparison tools to decide whether to continue with it.")

    return {
        "roadmap_type": "general",
        "title": f"Roadmap for {get_repo_name(repo)}",
        "steps": steps[:7],
    }


def generate_roadmap(repo: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    goal = _goal(profile)

    if "learn" in goal or "education" in goal:
        return generate_learning_roadmap(repo, profile)
    if "contribut" in goal or "open-source" in goal:
        return generate_contribution_roadmap(repo, profile)
    if "production" in goal or "use" in goal or "tool" in goal:
        return generate_production_roadmap(repo, profile)
    if "portfolio" in goal or "project" in goal:
        return generate_portfolio_roadmap(repo, profile)

    # fallback based on repo intent
    enriched = enrich_repo(repo)
    intents = enriched.get("repo_intents", {})
    strongest = max(intents.items(), key=lambda x: x[1])[0] if intents else ""
    if strongest == "learning":
        return generate_learning_roadmap(repo, profile)
    if strongest == "contribution":
        return generate_contribution_roadmap(repo, profile)
    if strongest == "production":
        return generate_production_roadmap(repo, profile)

    return generate_general_roadmap(repo, profile)
