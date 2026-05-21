from typing import Optional

from pydantic import BaseModel, Field


class ProfileContext(BaseModel):
    project_type: Optional[str] = None
    language: Optional[str] = None
    goal: Optional[str] = None
    level: Optional[str] = None
    repo_kind: Optional[str] = None
    complexity: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    candidate_pool: int = Field(default=200, ge=10, le=2000)

    language: Optional[str] = None
    license_name: Optional[str] = None
    min_stars: Optional[int] = Field(default=None, ge=0)
    topic: Optional[str] = None

    profile: Optional[ProfileContext] = None


class RecommendRequest(BaseModel):
    repo_identifier: str = Field(..., min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    same_language_only: bool = False


class ExplainRequest(BaseModel):
    query: str = Field(..., min_length=1)
    repo_identifier: str = Field(..., min_length=1)
    profile: Optional[ProfileContext] = None
