from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProfileRecommendRequest(BaseModel):
    project_type: Optional[str] = None
    language: Optional[str] = None
    goal: Optional[str] = None
    level: Optional[str] = None
    repo_kind: Optional[str] = None
    complexity: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=20)


class ProfileSearchRequest(ProfileRecommendRequest):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=20)
