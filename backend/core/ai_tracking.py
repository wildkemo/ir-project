"""AI request tracking helper for optional authenticated usage."""

import time
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from backend.core.history_service import record_ai_request
from backend.models.user import User

T = TypeVar("T")


def track_ai_request(
    db: Session,
    user: User | None,
    request_type: str,
    repo_identifier: str | None,
    fn: Callable[[], T],
    model: str | None = None,
) -> T:
    """Execute an AI function and record latency for authenticated users."""
    start = time.perf_counter()
    result = fn()
    if user is not None:
        latency_ms = (time.perf_counter() - start) * 1000
        resolved_model = model
        if isinstance(result, dict) and result.get("model"):
            resolved_model = str(result["model"])
        record_ai_request(db, user, request_type, repo_identifier, resolved_model, latency_ms)
    return result


def repo_identifier_from_payload(repo: dict[str, Any] | None) -> str | None:
    if not repo:
        return None
    return repo.get("full_name") or repo.get("name")
