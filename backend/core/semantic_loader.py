import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from repo_utils import is_github_repository, resolve_full_name
from semantic_hybrid_recommender import SemanticHybridRecommender
from smart_profile_recommender_v2 import UserProfile

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = ROOT / "processed.json"
EMBEDDINGS_PATH = ROOT / "repo_embeddings.npy"

_hybrid: Optional[SemanticHybridRecommender] = None


def load_semantic_hybrid() -> SemanticHybridRecommender:
    global _hybrid
    if _hybrid is None:
        _hybrid = SemanticHybridRecommender(
            data_path=str(PROCESSED_PATH),
            embeddings_path=str(EMBEDDINGS_PATH),
        )
    return _hybrid


def _github_full_name(url: str) -> Optional[str]:
    if not url:
        return None
    match = re.search(r"github\.com/([^/]+/[^/#?]+)", url, re.IGNORECASE)
    return match.group(1) if match else None


def profile_from_payload(payload: Optional[Dict[str, Any]]) -> Optional[UserProfile]:
    if not payload:
        return None
    has_any = any(
        payload.get(k)
        for k in (
            "project_type",
            "language",
            "goal",
            "level",
            "repo_kind",
            "complexity",
        )
    )
    if not has_any:
        return None
    return UserProfile(
        project_type=payload.get("project_type"),
        language=payload.get("language"),
        goal=payload.get("goal"),
        level=payload.get("level"),
        repo_kind=payload.get("repo_kind"),
        complexity=payload.get("complexity"),
        top_k=payload.get("top_k", 10),
    )


def normalize_search_result(item: Dict[str, Any], rank: int) -> Dict[str, Any]:
    breakdown = item.get("score_breakdown") or {}
    url = item.get("url") or ""
    doc_id = item.get("doc_id")
    full_name = item.get("full_name")

    if doc_id is not None:
        hybrid = load_semantic_hybrid()
        if 0 <= doc_id < len(hybrid.docs):
            full_name = resolve_full_name(hybrid.docs[doc_id]) or full_name

    full_name = full_name or _github_full_name(url) or item.get("title")

    return {
        "rank": rank,
        "score": item.get("score"),
        "bm25_score": breakdown.get("lexical_query_score"),
        "semantic_score": breakdown.get("semantic_similarity"),
        "phrase_score": 0.0,
        "metadata_score": breakdown.get("profile_match"),
        "id": item.get("doc_id"),
        "title": item.get("title"),
        "full_name": full_name,
        "url": url,
        "description": item.get("description"),
        "language": item.get("language"),
        "topics": item.get("topics") or [],
        "license": item.get("license"),
        "stars": item.get("stars", 0),
        "forks": item.get("forks", 0),
        "why_recommended": item.get("why_recommended") or [],
        "score_breakdown": breakdown,
        "mode": item.get("mode"),
    }


def hybrid_search(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    hybrid = load_semantic_hybrid()
    profile = profile_from_payload(payload.get("profile"))

    raw = hybrid.search(
        query=payload["query"],
        top_k=payload.get("top_k", 10),
        profile=profile,
        language=payload.get("language"),
        license_name=payload.get("license_name"),
        min_stars=payload.get("min_stars"),
        topic=payload.get("topic"),
        candidate_pool=payload.get("candidate_pool", 200),
    )

    filtered = [item for item in raw if is_github_repository(hybrid.docs[item["doc_id"]])]
    return [normalize_search_result(item, rank) for rank, item in enumerate(filtered, start=1)]
