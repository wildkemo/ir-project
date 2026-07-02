"""User preference model — experience level and license preferences."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class UserPreference(Base):
    """Core personalization settings for recommendation integration."""

    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_license: Mapped[str | None] = mapped_column(String(100), nullable=True)
    project_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    goal: Mapped[str | None] = mapped_column(String(100), nullable=True)
    repo_kind: Mapped[str | None] = mapped_column(String(100), nullable=True)
    complexity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<UserPreference user_id={self.user_id}>"
