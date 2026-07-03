"""Admin dashboard response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.auth_schema import UserResponse
from backend.schemas.history_schema import AIRequestResponse


class AdminStatsResponse(BaseModel):
    total_users: int
    total_searches: int
    total_recommendations: int
    total_ai_requests: int
    ollama_connected: bool = False
    qdrant_connected: bool = False


class TopSearchQuery(BaseModel):
    query: str
    count: int


class AdminAnalyticsResponse(BaseModel):
    top_search_queries: list[TopSearchQuery] = Field(default_factory=list)
    total_searches: int = 0
    total_recommendations: int = 0
    total_ai_requests: int = 0
    ai_request_types: dict[str, int] = Field(default_factory=dict)


class AdminUserListResponse(BaseModel):
    users: list[UserResponse]
    count: int


class AdminAILogsResponse(BaseModel):
    logs: list[AIRequestResponse]
    count: int
