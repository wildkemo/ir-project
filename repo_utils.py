"""Helpers to distinguish real GitHub repositories from topic/sponsor pages."""

import re
from typing import Any, Dict, List, Optional

NON_REPO_PATH_PREFIXES = ("topics", "sponsors", "collections", "orgs", "organizations")


def is_github_repository(doc: Dict[str, Any]) -> bool:
    """True only for owner/repo pages, not github.com/topics/... listings."""
    url = str(doc.get("url") or "").lower().strip()
    full_name = str(doc.get("full_name") or "").lower().strip()

    if not url and not full_name:
        return False

    if "/topics/" in url or full_name.startswith("topics/"):
        return False

    if "/sponsors/" in url or full_name.startswith("sponsors/"):
        return False

    match = re.search(r"github\.com/([^/?#]+/[^/?#]+)", url, re.IGNORECASE)
    if match:
        owner, name = match.group(1).lower().split("/", 1)
        if owner in NON_REPO_PATH_PREFIXES:
            return False
        if name in NON_REPO_PATH_PREFIXES:
            return False
        return True

    if full_name and "/" in full_name:
        owner = full_name.split("/", 1)[0]
        if owner in NON_REPO_PATH_PREFIXES:
            return False
        return True

    return False


def resolve_full_name(doc: Dict[str, Any]) -> Optional[str]:
    """Best owner/repo identifier for display and similar-repo lookup."""
    full_name = doc.get("full_name")
    if full_name:
        fn = str(full_name)
        lower = fn.lower()
        if "/" in fn and not lower.startswith("topics/") and not lower.startswith("sponsors/"):
            owner = lower.split("/", 1)[0]
            if owner not in NON_REPO_PATH_PREFIXES:
                return fn

    url = doc.get("url") or ""
    match = re.search(r"github\.com/([^/]+/[^/#?]+)", url, re.IGNORECASE)
    if not match:
        return full_name or doc.get("title")

    candidate = match.group(1)
    owner = candidate.split("/", 1)[0].lower()
    if owner in NON_REPO_PATH_PREFIXES:
        return doc.get("title") or None

    return candidate


def repository_docs(docs: list) -> List[Dict[str, Any]]:
    """Return only real repository records from processed.json."""
    return [doc for doc in docs if is_github_repository(doc)]
