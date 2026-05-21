import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from repo_utils import is_github_repository, resolve_full_name
from smart_profile_recommender_v2 import (
    DatasetOptionsBuilder,
    SmartProfileRecommender,
    UserProfile,
)

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = ROOT / "processed.json"
OPTIONS_PATH = ROOT / "smart_profile_options.json"

_recommender: Optional[SmartProfileRecommender] = None
_options_cache: Optional[Dict[str, Any]] = None

PROFILE_QUESTIONS = [
    {
        "id": "project_type",
        "title": "What type of project are you looking for?",
        "options_key": "project_types",
        "allow_skip": True,
    },
    {
        "id": "language",
        "title": "Which programming language do you prefer?",
        "options_key": "languages",
        "allow_skip": True,
    },
    {
        "id": "goal",
        "title": "What is your goal?",
        "options_key": "goals",
        "allow_skip": True,
    },
    {
        "id": "level",
        "title": "What is your skill level?",
        "options_key": "levels",
        "allow_skip": True,
    },
    {
        "id": "repo_kind",
        "title": "What kind of repository do you prefer?",
        "options_key": "repo_kinds",
        "allow_skip": True,
    },
    {
        "id": "complexity",
        "title": "How complex should the project be?",
        "options_key": "complexities",
        "allow_skip": True,
    },
]


def load_profile_recommender() -> SmartProfileRecommender:
    global _recommender
    if _recommender is None:
        _recommender = SmartProfileRecommender(str(PROCESSED_PATH))
    return _recommender


def get_raw_profile_options() -> Dict[str, Any]:
    global _options_cache
    if _options_cache is not None:
        return _options_cache

    if OPTIONS_PATH.exists():
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            _options_cache = json.load(f)
        return _options_cache

    builder = DatasetOptionsBuilder(str(PROCESSED_PATH))
    _options_cache = builder.save_website_options(str(OPTIONS_PATH))
    return _options_cache


def get_profile_questions_payload() -> Dict[str, Any]:
    raw = get_raw_profile_options()
    questions = []

    for spec in PROFILE_QUESTIONS:
        options = raw.get(spec["options_key"], [])
        questions.append(
            {
                "id": spec["id"],
                "title": spec["title"],
                "allow_skip": spec["allow_skip"],
                "options": [
                    {
                        "label": opt.get("label", opt.get("value", "")),
                        "value": opt.get("value"),
                        "count": opt.get("count"),
                    }
                    for opt in options
                ],
            }
        )

    return {"questions": questions}


def _github_full_name(url: str) -> Optional[str]:
    if not url:
        return None
    match = re.search(r"github\.com/([^/]+/[^/#?]+)", url, re.IGNORECASE)
    return match.group(1) if match else None


def normalize_profile_result(item: Dict[str, Any], rank: int, doc: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = item.get("url") or ""
    full_name = item.get("full_name")
    if doc:
        full_name = resolve_full_name(doc) or full_name
    full_name = full_name or _github_full_name(url) or item.get("title")

    return {
        "rank": rank,
        "score": item.get("score"),
        "title": item.get("title"),
        "full_name": full_name,
        "url": url,
        "description": item.get("description"),
        "language": item.get("language"),
        "topics": item.get("topics") or [],
        "stars": item.get("stars", 0),
        "forks": item.get("forks", 0),
        "why_recommended": item.get("why_recommended") or [],
        "score_breakdown": item.get("score_breakdown") or {},
        "mode": item.get("mode"),
        "doc_id": item.get("doc_id"),
    }


def build_user_profile(payload: Dict[str, Any]) -> UserProfile:
    return UserProfile(
        project_type=payload.get("project_type"),
        language=payload.get("language"),
        goal=payload.get("goal"),
        level=payload.get("level"),
        repo_kind=payload.get("repo_kind"),
        complexity=payload.get("complexity"),
        top_k=payload.get("top_k", 10),
    )


def recommend_for_profile(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    recommender = load_profile_recommender()
    profile = build_user_profile(payload)
    target = payload.get("top_k", 10)
    profile.top_k = min(len(recommender.docs), max(target * 10, 50))

    raw_results = recommender.recommend_for_profile(profile)
    filtered: List[Dict[str, Any]] = []

    for item in raw_results:
        doc_id = item.get("doc_id")
        if doc_id is None or doc_id >= len(recommender.docs):
            continue
        doc = recommender.docs[doc_id]
        if not is_github_repository(doc):
            continue
        filtered.append((item, doc))
        if len(filtered) >= target:
            break

    return [
        normalize_profile_result(item, rank, doc)
        for rank, (item, doc) in enumerate(filtered, start=1)
    ]


def search_with_profile(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    recommender = load_profile_recommender()
    profile = build_user_profile(payload)
    query = payload["query"]
    target = payload.get("top_k", 10)
    profile.top_k = min(len(recommender.docs), max(target * 10, 50))

    raw_results = recommender.search_with_profile(query, profile)
    filtered: List[Dict[str, Any]] = []

    for item in raw_results:
        doc_id = item.get("doc_id")
        if doc_id is None or doc_id >= len(recommender.docs):
            continue
        doc = recommender.docs[doc_id]
        if not is_github_repository(doc):
            continue
        filtered.append((item, doc))
        if len(filtered) >= target:
            break

    return [
        normalize_profile_result(item, rank, doc)
        for rank, (item, doc) in enumerate(filtered, start=1)
    ]
