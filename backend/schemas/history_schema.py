"""Favorites and history schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from backend.core.validators import sanitize_repo_identifier


class FavoriteRequest(BaseModel):
    repo_identifier: str = Field(..., min_length=3, max_length=255)

    @field_validator("repo_identifier")
    @classmethod
    def validate_repo(cls, value: str) -> str:
        return sanitize_repo_identifier(value)


class FavoriteResponse(BaseModel):
    id: uuid.UUID
    repo_identifier: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchHistoryResponse(BaseModel):
    id: uuid.UUID
    query: str
    search_type: str
    result_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationHistoryResponse(BaseModel):
    id: uuid.UUID
    repo_identifier: str
    recommendation_score: float | None = None
    recommendation_reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIRequestResponse(BaseModel):
    id: uuid.UUID
    request_type: str
    repo_identifier: str | None = None
    model: str | None = None
    latency_ms: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
