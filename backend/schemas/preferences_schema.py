"""User preference schemas."""

from pydantic import BaseModel, Field


class UserPreferencesRequest(BaseModel):
    experience_level: str | None = Field(default=None, max_length=50)
    preferred_license: str | None = Field(default=None, max_length=100)
    project_type: str | None = Field(default=None, max_length=100)
    goal: str | None = Field(default=None, max_length=100)
    repo_kind: str | None = Field(default=None, max_length=100)
    complexity: str | None = Field(default=None, max_length=50)
    languages: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)


class UserPreferencesResponse(BaseModel):
    experience_level: str | None = None
    preferred_license: str | None = None
    project_type: str | None = None
    goal: str | None = None
    repo_kind: str | None = None
    complexity: str | None = None
    languages: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
