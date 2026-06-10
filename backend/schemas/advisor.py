from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExplainRepoRequest(BaseModel):
    repo: Dict[str, Any]
    profile: Optional[Dict[str, Any]] = None
    query: Optional[str] = None
    score_breakdown: Optional[Dict[str, float]] = None
    include_roadmap: bool = True


class RoadmapRequest(BaseModel):
    repo: Dict[str, Any]
    profile: Optional[Dict[str, Any]] = None


class CompareReposRequest(BaseModel):
    repo_a: Dict[str, Any]
    repo_b: Dict[str, Any]
    profile: Optional[Dict[str, Any]] = None
    query: Optional[str] = None


class AdvisorSummaryRequest(BaseModel):
    query: str
    profile: Dict[str, Any] = Field(default_factory=dict)
    results: List[Dict[str, Any]]
    top_k: int = 5
