"""User profile update schemas."""

from pydantic import BaseModel, Field, field_validator


class UserUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    avatar: str | None = Field(default=None, max_length=512)
    bio: str | None = Field(default=None, max_length=2000)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        if value is None:
            return None
        from backend.core.validators import sanitize_username

        return sanitize_username(value)
