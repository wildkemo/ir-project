import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from repo_utils import is_github_repository, resolve_full_name
from semantic_hybrid_recommender import SemanticHybridRecommender
from smart_profile_recommender_v2 import UserProfile

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = ROOT / "processed.json"
VECTOR_DB_PATH = ROOT / "vector_db"

_hybrid: Optional[SemanticHybridRecommender] = None


def load_semantic_hybrid() -> SemanticHybridRecommender:
    global _hybrid
    if _hybrid is None:
        _hybrid = SemanticHybridRecommender(
            data_path=str(PROCESSED_PATH),
            vector_db_path=str(VECTOR_DB_PATH),
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


def _enrich_query(query: str, profile: Optional[UserProfile]) -> str:
    if not profile:
        return query
    profile.expand_topics_from_project_type()
    extra = profile.to_profile_query()
    if not extra:
        return query
    return f"{query} {extra}".strip()


def _map_score_breakdown(breakdown: Dict[str, Any]) -> Dict[str, Any]:
    """Map engine keys to API/frontend field names."""
    return {
        "lexical_query_score": breakdown.get("bm25"),
        "semantic_similarity": breakdown.get("semantic_cosine"),
        "profile_match": breakdown.get("popularity"),
        "weights": breakdown.get("weights"),
    }


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
    mapped_breakdown = _map_score_breakdown(breakdown)

    return {
        "rank": rank,
        "score": item.get("score"),
        "bm25_score": mapped_breakdown.get("lexical_query_score"),
        "semantic_score": mapped_breakdown.get("semantic_similarity"),
        "phrase_score": 0.0,
        "metadata_score": mapped_breakdown.get("profile_match"),
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
        "score_breakdown": mapped_breakdown,
        "mode": item.get("mode"),
    }


def hybrid_search(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    hybrid = load_semantic_hybrid()
    profile = profile_from_payload(payload.get("profile"))
    query = _enrich_query(payload["query"], profile)

    raw = hybrid.search(
        query=query,
        top_k=payload.get("top_k", 10),
        language=payload.get("language"),
        license_name=payload.get("license_name"),
        min_stars=payload.get("min_stars"),
        topic=payload.get("topic"),
        candidate_pool=payload.get("candidate_pool", 200),
    )

    filtered = [item for item in raw if is_github_repository(hybrid.docs[item["doc_id"]])]
    return [normalize_search_result(item, rank) for rank, item in enumerate(filtered, start=1)]


def explain_result(
    *,
    query: str,
    repo_identifier: str,
    profile: Optional[UserProfile] = None,
) -> Dict[str, Any]:
    hybrid = load_semantic_hybrid()
    enriched_query = _enrich_query(query, profile)

    idx = hybrid.find_repo_index(repo_identifier)
    if idx is None:
        raise ValueError(f"Repository not found: {repo_identifier}")

    doc = hybrid.docs[idx]
    bm25 = float(hybrid.bm25_scores(enriched_query)[idx])
    semantic = float(hybrid.semantic_scores(enriched_query)[idx])
    popularity = float(hybrid.popularity_scores()[idx])

    final = (
        hybrid.bm25_weight * bm25
        + hybrid.semantic_weight * semantic
        + hybrid.popularity_weight * popularity
    )

    return {
        "query": query,
        "enriched_query": enriched_query if enriched_query != query else None,
        "repo": resolve_full_name(doc) or repo_identifier,
        "final_score": round(final, 6),
        "bm25_contribution": round(hybrid.bm25_weight * bm25, 6),
        "semantic_contribution": round(hybrid.semantic_weight * semantic, 6),
        "profile_contribution": round(hybrid.popularity_weight * popularity, 6),
        "raw_parts": {
            "bm25_score": round(bm25, 6),
            "semantic_score": round(semantic, 6),
            "profile_score": round(popularity, 6),
        },
        "why_recommended": hybrid.explain_match(
            query=enriched_query,
            doc=doc,
            bm25_score=bm25,
            semantic_score=semantic,
            popularity_score=popularity,
        ),
    }


def recommend_similar(
    *,
    repo_identifier: str,
    top_k: int = 10,
    same_language_only: bool = False,
) -> List[Dict[str, Any]]:
    hybrid = load_semantic_hybrid()
    raw = hybrid.similar_repositories(
        repo_identifier,
        top_k=top_k,
        same_language_only=same_language_only,
    )
    results = []
    for item in raw:
        results.append(
            {
                **item,
                "similarity": item.get("semantic_cosine"),
            }
        )
    return results
