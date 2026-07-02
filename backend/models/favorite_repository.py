"""Favorite repository reference — stores owner/repo identifier only."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class FavoriteRepository(Base):
    """User-saved repository reference (no duplicated metadata)."""

    __tablename__ = "favorite_repositories"
    __table_args__ = (UniqueConstraint("user_id", "repo_identifier", name="uq_user_favorite"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    repo_identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="favorites")

    def __repr__(self) -> str:
        return f"<FavoriteRepository {self.repo_identifier!r}>"
