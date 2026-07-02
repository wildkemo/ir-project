"""User model — core authentication and profile identity."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.ai_request import AIRequest
    from backend.models.favorite_repository import FavoriteRepository
    from backend.models.preferred_framework import PreferredFramework
    from backend.models.preferred_language import PreferredLanguage
    from backend.models.preferred_topic import PreferredTopic
    from backend.models.recommendation_history import RecommendationHistory
    from backend.models.refresh_token import RefreshToken
    from backend.models.role import Role
    from backend.models.search_history import SearchHistory
    from backend.models.user_preference import UserPreference


class User(Base):
    """Registered application user."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    preferences: Mapped["UserPreference | None"] = relationship(
        "UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    preferred_languages: Mapped[List["PreferredLanguage"]] = relationship(
        "PreferredLanguage", back_populates="user", cascade="all, delete-orphan"
    )
    preferred_topics: Mapped[List["PreferredTopic"]] = relationship(
        "PreferredTopic", back_populates="user", cascade="all, delete-orphan"
    )
    preferred_frameworks: Mapped[List["PreferredFramework"]] = relationship(
        "PreferredFramework", back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[List["FavoriteRepository"]] = relationship(
        "FavoriteRepository", back_populates="user", cascade="all, delete-orphan"
    )
    search_history: Mapped[List["SearchHistory"]] = relationship(
        "SearchHistory", back_populates="user", cascade="all, delete-orphan"
    )
    recommendation_history: Mapped[List["RecommendationHistory"]] = relationship(
        "RecommendationHistory", back_populates="user", cascade="all, delete-orphan"
    )
    ai_requests: Mapped[List["AIRequest"]] = relationship(
        "AIRequest", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User username={self.username!r}>"
