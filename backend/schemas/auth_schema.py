"""Authentication request/response schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.core.validators import sanitize_email, sanitize_username


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return sanitize_username(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return sanitize_email(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return sanitize_email(value)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    avatar: str | None = None
    bio: str | None = None
    role: RoleResponse
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
