"""AI request tracking helper for optional authenticated usage."""

import time
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from backend.core.history_service import record_ai_request
from backend.models.user import User

T = TypeVar("T")

_MAX_USER_MESSAGE = 4000
_MAX_AI_RESPONSE = 16000


def _truncate(text: str | None, limit: int) -> str | None:
    if text is None:
        return None
    cleaned = text.strip()
    if not cleaned:
        return None
    return cleaned[:limit]


def extract_ai_response(result: Any) -> str | None:
    """Serialize an AI endpoint result into storable response text."""
    if not isinstance(result, dict):
        return str(result) if result is not None else None

    for key in ("answer", "summary", "recommendation"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    if result.get("repo_name") and isinstance(result.get("summary"), str):
        parts = [result["summary"]]
        if result.get("best_for"):
            parts.append(f"Best for: {result['best_for']}")
        strengths = result.get("strengths") or []
        if strengths:
            parts.append("Strengths:\n" + "\n".join(f"• {s}" for s in strengths))
        weaknesses = result.get("weaknesses") or []
        if weaknesses:
            parts.append("Considerations:\n" + "\n".join(f"• {w}" for w in weaknesses))
        return "\n\n".join(parts)

    steps = result.get("steps")
    if isinstance(steps, list) and steps:
        title = result.get("title") or "Roadmap"
        lines = [title, ""]
        for index, step in enumerate(steps, start=1):
            if isinstance(step, str):
                lines.append(f"{index}. {step}")
            elif isinstance(step, dict):
                label = step.get("title") or step.get("name") or step.get("description") or str(step)
                lines.append(f"{index}. {label}")
        return "\n".join(lines)

    if result.get("winner") or result.get("comparison_table"):
        lines: list[str] = []
        if result.get("winner"):
            lines.append(f"Winner: {result['winner']}")
        if isinstance(result.get("recommendation"), str):
            lines.append(result["recommendation"])
        table = result.get("comparison_table") or []
        for row in table[:10]:
            if isinstance(row, dict):
                metric = row.get("metric") or row.get("label") or "Metric"
                a_val = row.get("repo_a") or row.get("a") or ""
                b_val = row.get("repo_b") or row.get("b") or ""
                lines.append(f"{metric}: {a_val} vs {b_val}")
        return "\n\n".join(lines) if lines else None

    return None


def extract_response_mode(result: Any) -> str | None:
    if isinstance(result, dict):
        mode = result.get("mode") or result.get("roadmap_type")
        return str(mode) if mode else None
    return None


def track_ai_request(
    db: Session,
    user: User | None,
    request_type: str,
    repo_identifier: str | None,
    fn: Callable[[], T],
    model: str | None = None,
    user_message: str | None = None,
) -> T:
    """Execute an AI function and record latency plus content for authenticated users."""
    start = time.perf_counter()
    result = fn()
    if user is not None:
        latency_ms = (time.perf_counter() - start) * 1000
        resolved_model = model
        if isinstance(result, dict) and result.get("model"):
            resolved_model = str(result["model"])
        record_ai_request(
            db,
            user,
            request_type,
            repo_identifier,
            resolved_model,
            latency_ms,
            user_message=_truncate(user_message, _MAX_USER_MESSAGE),
            ai_response=_truncate(extract_ai_response(result), _MAX_AI_RESPONSE),
            response_mode=extract_response_mode(result),
        )
    return result


def repo_identifier_from_payload(repo: dict[str, Any] | None) -> str | None:
    if not repo:
        return None
    return repo.get("full_name") or repo.get("name")
